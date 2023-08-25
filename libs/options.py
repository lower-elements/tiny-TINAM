import json
import os
from . import consts

# defaults.
prefs = {
    "beacons": True,
    "buffer_timing": 2,
}

def load():
    try:
        with open("./settings.json", "rb") as f:
            global prefs
            loaded_prefs = json.loads(f.read().decode())
            for key, value in loaded_prefs.items():
                prefs[key] = value
    except FileNotFoundError:
        # settings file not found, create one with the default settings.
        save()


def save():
    with open("./settings.json", "wb") as f:
        f.write(json.dumps(prefs).encode())


def get(key, default=None):
    return prefs.get(key, default)


def set(key, value, autosave=True):
    prefs[key] = value
    if autosave:
        save()
