from .. import audio, consts
from ..speech import speak
from .entity import Entity
from random import randint as random


class Player(Entity):
    def __init__(self, game, map, x, y, z, hp=100):
        super().__init__(game, map, x, y, z, hp, "player")
        self.locked = False
        self.direct_src = audio.Src(direct=True)
        self.play_direct = self.direct_src.play_sound
        self.walktime = 270
        self.runtime = 184
        self.movetime = self.walktime
        self.turntime = 5
        self.turning_clock = game.new_clock()

    def death(self):
        pass

    def fall_stop(self):
        super().fall_stop()
        self.hp = self.hp - (self.fall_distance / 2 + random(-3, 3))
        self.fall_distance = 0
