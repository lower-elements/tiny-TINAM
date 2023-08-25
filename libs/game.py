import sys
import weakref
from collections import namedtuple
import contextlib
import pygame
from .speech import speak
from . import options, state, virtual_input, menus, clock, gameplay, consts, audio, speech
from .os_tools import get_os

Delayed_function = namedtuple("delayed_function", ["clock", "time", "function"])


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.clocks = weakref.WeakSet()
        options.load()
        self.framerate = 60
        self.delta = 1 / self.framerate * 1000
        self.clock = pygame.time.Clock()
        self.stack = []
        self.events = []
        self.input_history = [""]
        self.input = virtual_input.Virtual_input(self)
        self.last_fps = 60
        self.delayed_functions = {}
        self.ids = 0

    def start_game(self):
        self.replace(gameplay.Gameplay(self))

    def start(self):
        menus.main_menu(self)

    def new_id(self):
        self.ids += 1
        return self.ids

    def call_after(self, time, function):  # sourcery skip: avoid-builtin-shadow
        """call{function} after {time}ms. returns an id that you could use to stop a function before its executed"""
        id = self.new_id()
        delayed_function = Delayed_function(self.new_clock(), time, function)
        self.delayed_functions[id] = delayed_function
        return id

    def cancel_before(self, id):
        """takes an id and prevents the delayed function of that id (if any) from running if they havent been ran yet."""
        if self.delayed_functions[id]:
            del self.delayed_functions[id]

    def toggle(self, key, on_text="on", off_text="off"):
        """toggle options[key]. speaks the new state(whether on or off)"""
        if option := options.get(key):
            speak(off_text)
            options.set(key, False)
            return False
        else:
            speak(on_text)
            options.set(key, True)
            return True

    def toggle_state(self, text, key):
        """returns {text} and whether its on or off. for example: test. off"""
        st = "on" if options.get(key) else "off"
        return f"{text}. {st}"

    def toggle_item(self, text, key):
        """returns a tuple to toggle {key} with the title as {text}. the tuple is accepted by Menu as a menu item only."""
        return (lambda: self.toggle_state(text, key), lambda: self.toggle(key))

    def exit(self):
        self.stack = []

    def new_clock(self):
        cl = clock.Clock()
        self.clocks.add(cl)
        return cl

    def loop(self):
        while True:
            self.update(self.delta)
            self.events = pygame.event.get()
            for event in self.events:
                if (
                    event.type == pygame.KEYDOWN
                    and event.mod & pygame.KMOD_CTRL
                    and get_os() == consts.OS_LINUX
                ):
                    speech.linux_speaker.cancel()
            audio.loop()
            if len(self.stack) == 0:
                options.save()
                pygame.quit()
                sys.exit()
            st = self.stack[-1]
            if isinstance(st, state.State):
                st.update(self.events)
            elif callable(st):
                st()
            self.last_fps = round(self.clock.get_fps())
            ids_to_remove = []
            for i in self.delayed_functions.copy():
                if (
                    self.delayed_functions[i].clock.elapsed
                    >= self.delayed_functions[i].time
                ):
                    if callable(self.delayed_functions[i].function):
                        self.delayed_functions[i].function()
                    ids_to_remove.append(i)
            for i in ids_to_remove:
                del self.delayed_functions[i]
            self.delta = self.clock.tick(self.framerate)
            self.update(self.delta)

    def update(self, delta):
        for i in self.clocks:
            i.update(delta)

    def pop(self):
        with contextlib.suppress(IndexError):
            prev = self.stack.pop()
            if isinstance(prev, state.State):
                prev.exit()
            return prev

    def append(self, st):
        self.stack.append(st)
        if isinstance(st, state.State):
            st.enter()
        return st

    def replace(self, st):
        self.pop()
        return self.append(st)

    def cancel(self, message="Canceled."):
        self.pop()
        speak(message)
