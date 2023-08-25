import functools
from . import menu, speech, virtual_input, options, consts, audio
from .os_tools import get_os
import pygame


def linux_change_speech_module(game):
    def set_module(module):
        speech.linux_speaker.set_output_module(module)

    modules_menu = menu.Menu(game, "Select your speech module")
    set_default_sounds(modules_menu)
    items = []
    for i in speech.linux_speaker.list_output_modules():
        items.append((i, functools.partial(set_module, i)))
    items.append(("Back", game.pop))
    modules_menu.add_items(items)
    game.append(modules_menu)


def linux_change_rate(game):
    def set_rate(rate):
        try:
            speech.linux_speaker.set_rate(int(rate))
            speech.speak("Done!")
        except ValueError:
            speech.speak("Input a valid number please?")
        game.pop()

    game.append(game.input.run("Input the rate you want to set", handeler=set_rate))


def linux_change_pitch(game):
    def set_pitch(pitch):
        try:
            speech.linux_speaker.set_pitch(int(pitch))
        except ValueError:
            speech.speak("Input a valid number please?")
        game.pop()

    game.append(game.input.run("Input the pitch you want to set", handeler=set_pitch))


def linux_change_volume(game):
    def set_volume(volume):
        try:
            speech.linux_speaker.set_volume(int(volume))
        except ValueError:
            speech.speak("Input a valid number please?")
        game.pop()

    game.append(game.input.run("Input the volume you want to set", handeler=set_volume))


def main_menu(game):
    """replace the current game state with the main menu."""
    m = menu.Menu(
        game,
        "Main menu.",
    )
    set_default_sounds(m)
    m.add_items(
        (
            ("Start Game", game.start_game),
            ("options", lambda: options_menu(game)),
            ("Exit", game.exit),
        )
    )
    game.replace(m)


def options_menu(game):
    """append the options menu to the games stack."""
    m = menu.Menu(game, "Options menu")
    set_default_sounds(m)
    items = [
        (
            "Set how you would like timestamps in the end of buffer items to be displayed",
            lambda: buffer_timing_menu(game),
        ),
        (
            "Set which Head Relay Transform Model you would like to use. Currently set to "
            + str(options.get("hrtf_model", 3)),
            lambda: hrtf_model_menu(game),
        ),
    ]
    if get_os() == consts.OS_LINUX:
        items.extend(
            (
                ("Change TTS module", lambda: linux_change_speech_module(game)),
                ("Change TTS rate", lambda: linux_change_rate(game)),
                ("Change TTS volume", lambda: linux_change_volume(game)),
                ("Change TTS pitch", lambda: linux_change_pitch(game)),
            )
        )

    items.append(("Back", game.pop))
    m.add_items(items)
    game.append(m)


def buffer_timing_menu(game):
    """append the buffer time display menu to the games stack."""
    m = menu.Menu(
        game,
        "How would you like timestamps to be displayed in buffer items?",
        autoclose=True,
    )
    set_default_sounds(m)
    m.add_items(
        (
            ("Absolute time", lambda: options.set("buffer_timing", 1)),
            ("Relative time", lambda: options.set("buffer_timing", 2)),
            ("Don't display timestamps", lambda: options.set("buffer_timing", 3)),
            ("Back", lambda: 0),
        )
    )
    game.append(m)


def hrtf_model_menu(game):
    m = menu.Menu(game, "Select your Head Relay Transform Function model")
    set_default_sounds(m)
    m.add_items(
        [
            ("HRTF model 1", lambda: set_hrtf_model(1, game)),
            ("HRTF model 2", lambda: set_hrtf_model(2, game)),
            ("HRTF model 3", lambda: set_hrtf_model(3, game)),
            ("No HRTF model", lambda: set_hrtf_model(None, game)),
            ("go back", lambda: game.pop()),
        ]
    )
    game.append(m)


def set_hrtf_model(model, game):
    audio.listener.hrtf = model
    options.set("hrtf_model", model)
    game.pop()


def set_default_sounds(m):
    pass
    # m.set_sounds(
    #     click="menu/move.ogg",
    #     enter="menu/select.ogg",
    #     open="menu/open.ogg",
    #     close="menu/close.ogg",
    # )
