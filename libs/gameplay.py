import pygame
from .speech import speak
from . import state, world_map, camera, options, buffer, audio, menus, menu
from .objects import player


class Gameplay(state.State):
    def __init__(self, game):
        super().__init__(game)
        self.map = world_map.Map(self.game, 0, 0, 0, 10, 10, 10)
        self.player = player.Player(self.game, self.map, 0, 0, 0)
        self.camera = camera.Camera(self.game)
        self.camera.set_focus_object(self.player)
        self.music_volume = options.get("music_volume", 25)
        self.running = False
        self.turning = False
        self.can_run = True
        self.keys_held = {}
        self.keys_pressed = {
            pygame.K_COMMA: self.buffer_move_l,
            pygame.K_PERIOD: self.buffer_move_r,
            pygame.K_LEFTBRACKET: self.buffer_cycle_l,
            pygame.K_RIGHTBRACKET: self.buffer_cycle_r,
            pygame.K_ESCAPE: self.ask_to_exit,
            pygame.K_F11: self.speak_fps,
            pygame.K_BACKSLASH: lambda mod: buffer.toggle_mute(),
            pygame.K_END: self.music_down,
            pygame.K_HOME: self.music_up,
        }
        self.keys_released = {}

    def enter(self):
        super().enter()
        self.ambience = audio.Src(direct=True)

    def exit(self):
        super().exit()
        self.ambience.destroy()
        self.map.destroy()

    def update(self, events):
        self.player.loop()
        self.map.loop()
        should_block = super().update(events)
        if should_block is True:
            # some substate doesnt want us to handel events for now.
            return
        elif isinstance(should_block, list):
            events = should_block
        key = pygame.key.get_pressed()
        for i in self.keys_held:
            if key[i]:
                self.keys_held[i](pygame.key.get_mods())
        for event in events:
            if event.type == pygame.KEYDOWN and event.key in self.keys_pressed:
                self.keys_pressed[event.key](event.mod)
            elif event.type == pygame.KEYUP and event.key in self.keys_released:
                self.keys_released[event.key](event.mod)

    def buffer_move_l(self, mod):
        if mod & pygame.KMOD_SHIFT:
            return buffer.cycle_item(3)
        buffer.cycle_item(1)

    # key event handelers:
    def buffer_move_r(self, mod):
        if mod & pygame.KMOD_SHIFT:
            return buffer.cycle_item(4)
        buffer.cycle_item(2)

    def buffer_cycle_l(self, mod):
        if mod & pygame.KMOD_SHIFT:
            return buffer.cycle(3)
        buffer.cycle(1)

    def buffer_cycle_r(self, mod):
        if mod & pygame.KMOD_SHIFT:
            return buffer.cycle(4)
        buffer.cycle(2)

    def quit(self, mod):
        menus.main_menu(self.game)

    def speak_fps(self, mod):
        speak(f"{self.game.last_fps} FPS")

    def ask_to_exit(self, mod):
        m = menu.Menu(
            self.game,
            "Are you sure you want to exit?",
            autoclose=True,
            parrent=self,
        )
        items = [
            ("Yes", lambda: self.quit(mod)),
            ("No", lambda: None),
        ]
        m.add_items(items)
        menus.set_default_sounds(m)
        self.add_substate(m)

    def music_down(self, mod):
        if self.music_volume > 0:
            for i in self.map.music_list:
                # i.sound.fade(_from=self.music_volume, to=self.music_volume - 5, fade_time=i.fade_time / 2)
                i.sound.set_volume(self.music_volume - 5)

                i.volume -= 5
            self.music_volume -= 5
            options.set("music_volume", self.music_volume)
        speak(f"music volume: {str(self.music_volume * 2)} percent. ")

    def music_up(self, mod):
        if self.music_volume < 50:
            for i in self.map.music_list:
                # i.sound.fade(_from=self.music_volume, to=self.music_volume + 5, fade_time=i.fade_time / 2)
                i.sound.set_volume(self.music_volume + 5)

                i.volume += 5
            self.music_volume += 5
            options.set("music_volume", self.music_volume)
        speak(f"music volume: {str(self.music_volume * 2)} percent. ")
