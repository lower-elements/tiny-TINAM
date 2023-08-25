import os
import contextlib
from collections import namedtuple
import weakref
import pyogg
import urllib3
from . import openal
import enum
import math
from .consts import *
from .movement import get_3d_distance
from . import path_utils
from . import options

http = urllib3.PoolManager()
listener = openal.Listener()
# listener.distance_model = 3
listener.hrtf = options.get("HTRF_model", 3)
max_distance = 26
sources = weakref.WeakSet()
rolloff = 0.5
global_reverb = None
global_filter = None


def load_web_sound(url, path):
    with open(path, "wb") as f:
        f.write(http.request("GET", url).data)
        return path


class Filter:
    nothing = None
    lp = openal.lowpass_filter
    hp = openal.highpass_filter


buffers = {}


position = (0, 0, 0)


def move(x, y, z):
    global position
    position = (x, y, z)
    listener.position = position
    for i in sources:
        if not i.direct:
            with contextlib.suppress(Exception):
                i.mute_if_far()


def get_buffer(file):
    global buffers
    file_buffer = None
    if file in buffers:
        file_buffer = buffers[file]
    else:
        try:
            file_buffer = pyogg.VorbisFile(file)
            buffers[file] = file_buffer
        except Exception as e:
            print(file, e)
            file_buffer = None
            buffers[file] = file_buffer
    if file_buffer:
        buffer = openal.BufferSound()
        buffer.channels = file_buffer.channels
        buffer.bitrate = 16
        buffer.length = file_buffer.buffer_length
        buffer.samplerate = file_buffer.frequency
        buffer.duration = (file_buffer.buffer_length / float(file_buffer.frequency)) / 2
        buffer.load(file_buffer.buffer)
        return buffer


def deg2rad(angle):
    return (angle / 180.0) * math.pi


def make_orientation(hdegrees, vdegrees, bdegrees=0):
    hrad = deg2rad(hdegrees)
    vrad = deg2rad(vdegrees)
    return (math.sin(hrad), math.cos(hrad), -math.sin(vrad), 0, 0, 1)


def reverb(t60, damp=1500):
    if t60 is None:
        return t60
    r = openal.reverb()
    r.decay_time = t60
    r.gain = 0.2
    r.late_reverb_delay = 0
    slot = openal.EFXslot()
    slot.set_effect(r)
    slot.delete_effect = r.delete
    return slot


facing = 0


def turn(hdirection, vdirection, bdirection):
    global hfacing
    global vfacing
    global bfacing
    hfacing = hdirection
    vfacing = vdirection
    bfacing = bdirection
    orientation = make_orientation(hfacing, vfacing, bfacing)
    listener.at_orientation = orientation[:3]
    listener.up_orientation = orientation[3:]


class Sound:
    def __init__(
        self, src, buffer, generator, stream: bool = False, rel_x=0, rel_y=0, rel_z=0
    ):
        self.destroied = False
        self.src = src
        self.buffer = buffer
        self.generator = generator
        self.stream = stream
        self.rel_x = rel_x
        self.rel_y = rel_y
        self.rel_z = rel_z
        self.length = buffer.duration
        self.position = property(self.get_position, self.set_position)
        self.pause = self.generator.pause
        self.play = self.generator.play
        self.volume = 100

    def fade(self, *args, **kwargs):
        pass

    def get_position(self):
        return (self.generator.seek) * 100

    def set_position(self, position):
        self.generator.seek = (position) / 100

    def get_volume(self):
        return self.generator.volume * 100

    def set_volume(self, v):
        self.generator.volume = v / 100

    def destroy(self):
        if not self.destroied:
            self.destroied = True
            self.generator.delete()
            self.buffer.delete()
        self.src.sounds.discard(self)


class Src:
    def __init__(self, accept_effects=True, direct=False):
        self.muted = False
        self.sounds = set()
        self.x, self.y, self.z = 0, 0, 0
        self.direct = direct
        self.filter = None
        self.reverb = None
        self.accept_effects = accept_effects
        if accept_effects:
            if global_reverb:
                self.set_reverb(global_reverb)
            if global_filter:
                self.set_filter(global_filter)
        self.__del__ = self.destroy
        self.ids = {}
        sources.add(self)

    def play_sound(
        self,
        path,
        looping=False,
        volume=100,
        stream=False,
        id="",
        rel_x=0,
        rel_y=0,
        rel_z=0,
    ):
        if path.startswith("server:"):
            sound_name = path.split(":")[1]
            sound_path = f"server_sounds/{sound_name}"
            if not os.path.exists(
                f"{SOUNDPREPEND}/{sound_path}"
            ) or not os.path.getsize(f"{SOUNDPREPEND}/{sound_path}"):
                os.makedirs(os.path.dirname(f"data/{sound_path}"), exist_ok=True)
                load_web_sound(
                    f"{SERVER_SOUNDS_URL}{sound_name}", f"{SOUNDPREPEND}/{sound_path}"
                )
            return self.play_sound(
                sound_path, looping, volume, stream, id, rel_x, rel_y, rel_z
            )
        path = SOUNDPREPEND + path
        path = path_utils.random_item(path)
        buffer = get_buffer(path)
        if buffer is None:
            return
        generator = openal.Player()
        generator.add(buffer)
        if looping:
            generator.loop = True
        generator.volume = volume / 100
        if not self.direct:
            generator.rolloff = rolloff
            generator.position = (self.x + rel_x, self.y + rel_y, self.z + rel_z)
            generator.max_distance = max_distance
        else:
            generator.source_relative = True
        if self.filter:
            generator.add_filter(self.filter)
        if self.reverb:
            generator.add_effect(self.reverb)
        snd = Sound(self, buffer, generator, False, rel_x, rel_y, rel_z)
        if id:
            if id in self.ids:
                self.ids[id].destroy()
            self.ids[id] = snd
        self.sounds.add(snd)
        self.mute_if_far()
        generator.play()
        snd.volume = volume
        return snd

    def set_filter(self, filter):
        if self.accept_effects:
            for i in self.sounds.copy():
                if i.destroied:
                    return
                if self.filter and filter is None:
                    i.generator.del_filter(self.filter)
                else:
                    i.generator.add_filter(filter)
            self.filter = filter

    def set_reverb(self, _reverb=None, destroy_current=False):
        for i in self.sounds.copy():
            if i.destroied:
                return
            if self.reverb is not None:
                i.generator.del_effect(self.reverb)
            if _reverb:
                i.generator.add_effect(_reverb)
            self.reverb = _reverb

    def pause(self, value):
        for i in self.sounds.copy():
            if i.destroied:
                return
            if value:
                i.pause()
            else:
                i.play()

    def destroy(self, destroy_atached_reverb=False):
        if self.reverb:
            if destroy_atached_reverb:
                self.reverb.delete()
            else:
                self.set_reverb(None)
        sources.discard(self)
        for i in self.sounds.copy():
            if i.destroied:
                return
            i.destroy()

    def move(self, x, y, z):
        if self.direct:
            raise NotImplementedError("not supported with direct sources")
        self.x, self.y, self.z = x, y, z
        for i in self.sounds.copy():
            if i.destroied:
                return
            i.generator.position = (x + i.rel_x, y + i.rel_y, z + i.rel_z)
        self.mute_if_far()

    def mute_if_far(
        self,
    ):
        """
        If the distance between the listener and the sound source is greater than the maximum distance, mute
        the sound source. If the distance is less than the maximum distance, unmute the sound source
        """
        distance = get_3d_distance(*position, self.x, self.y, self.z)
        if distance > max_distance and not self.direct:
            self.muted = True
            for i in self.sounds:
                i.set_volume(0)
        elif distance <= max_distance and self.muted:
            self.muted = False
            for i in self.sounds:
                i.set_volume(i.volume)


def filter_all(f):
    for i in sources.copy():
        i.set_filter(f)


def set_global_filter(filter):
    global global_filter
    filter_all(filter)
    global_filter = filter


def filter_space(minx, maxx, miny, maxy, minz, maxz, inn=None, out=None):
    for i in sources.copy():
        position = i.src.position.value
        x = position[0]
        y = position[1]
        z = position[2]
        if (
            inn != None
            and x <= maxx
            and x >= minx
            and y <= maxy
            and y >= miny
            and z <= maxz
            and z >= minz
        ):
            i.filter(inn)
        elif (
            out != None
            and x > maxx
            and x < minx
            and y > maxy
            and y < miny
            and z > maxz
            and z < minz
        ):
            i.filter(out)


direct = Src(direct=True, accept_effects=False)
play_direct = direct.play_sound


def set_global_reverb(reverb, destroy_current=True):
    global global_reverb
    global_reverb = reverb
    for i in sources.copy():
        if i.accept_effects:
            i.set_reverb(reverb, destroy_current)


def loop():
    for source in sources.copy():
        for snd in source.sounds.copy():
            if not snd.generator.playing():
                snd.destroy()
