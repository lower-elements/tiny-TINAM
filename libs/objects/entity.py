import os
from random import randint as random

from .. import audio, movement, consts
from .object import Object


class Entity(Object):
    def __init__(self, game, map, x, y, z, hp, name="None"):
        super().__init__(game, map, x, y, z)
        self.on_move = None
        self.on_turn = None
        self.movement_clock = game.new_clock()
        self.hp = hp
        self.hfacing = 0
        self.vfacing = 0
        self.bfacing = 0
        self.fall_distance = 0
        self.name = name

    def move(self, x, y, z, play_sound=True, mode="walk"):
        self.x = x
        self.y = y
        self.z = z
        if callable(self.on_move):
            self.on_move(x, y, z)
        self.src.move(self.x, self.y, self.z)
        tile = self.map.get_tile_at(self.x, self.y, self.z)
        # start/stop falling if the current tile is air.
        if not self.falling and tile in ["air", ""]:
            self.fall_start()
        elif self.falling and tile not in ["air", ""]:
            self.fall_stop()
        if play_sound and not self.falling:
            if mode == "run" and not os.path.exists(
                f"{audio.SOUNDPREPEND}/steps/{tile}/run"
            ):
                mode = "walk"
            self.play_sound(
                f"steps/{tile}/{mode}",
                volume=80,
                rel_z=-1,
            )

    def face(self, hdeg, vdeg, bdeg=0, play_sound=False):
        if play_sound:
            self.play_sound("players/turn.ogg")
        self.hfacing = hdeg % 360
        self.vfacing = ((vdeg + 90) % 181) - 90
        self.bfacing = ((bdeg + 90) % 181) - 90
        if callable(self.on_turn):
            self.on_turn(self.hfacing, self.vfacing, self.bfacing)

    def walk(
        self, back=False, left=False, right=False, down=False, up=False, mode="walk"
    ):
        dist = movement.move((self.x, self.y, self.z), self.hfacing).get_tuple
        self.face(self.hfacing, 0)
        if back:
            dist = movement.move(
                (self.x, self.y, self.z), self.hfacing + 180 % 360
            ).get_tuple
        if left:
            dist = movement.move(
                (self.x, self.y, self.z), self.hfacing - 90 % 360
            ).get_tuple
        if right:
            dist = movement.move(
                (self.x, self.y, self.z), self.hfacing + 90 % 360
            ).get_tuple
        if down:
            dist = (self.x, self.y, self.z - 1)
        if up:
            dist = (self.x, self.y, self.z + 1)
        if self.map.in_bound(*dist):
            disttile = self.map.get_tile_at(*dist)
            if "wall" not in disttile:
                if (up or down) and disttile in ["air", ""]:
                    return False
                self.move(*dist, mode=mode)
                return True
            self.play_sound(
                f"walls/{disttile}.ogg",
                rel_x=dist[0] - self.x,
                rel_y=dist[1] - self.y,
                rel_z=1,
            )
        return False

    def fall_start(self):
        self.fall_clock.restart()
        self.play_sound("foley/fall/start.ogg")
        self.falling = True

    def fall_stop(self):
        self.falling = False
        self.play_sound("foley/fall/end.ogg")
        # sound-simulate landing hard on a platform.
        for _ in range(random(3, 7)):
            self.game.call_after(
                random(10, 100), lambda: self.move(self.x, self.y, self.z, mode="run")
            )

    def loop(self):
        if (
            self.falling
            and self.fall_clock.elapsed >= self.fall_time
            and self.map.in_bound(self.x, self.y, self.z)
        ):
            self.fall_clock.restart()
            self.move(self.x, self.y, self.z - 1, False)
            self.face(random(-45, 45), random(-45, 45), random(-45, 45))
            self.fall_distance += 1
            if not self.map.in_bound(self.x, self.y, self.z):
                self.fall_stop()

    def on_hit(self):
        self.play_sound(f"entities/{self.name}/pain{random(1, 3)}.ogg)")

    def death(self):
        raise NotImplementedError
