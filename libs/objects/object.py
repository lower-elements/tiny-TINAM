import contextlib
from .. import audio


class Object:
    def __init__(self, game, map, x, y, z):
        self.game = game
        self.map = map
        self.x = x
        self.y = y
        self.z = z
        self.falling = False
        self.fall_time = 80
        self.fall_clock = game.new_clock()
        self.src = audio.Src()
        self.src.move(x, y, z)

    def play_sound(
        self, sound, looping=False, volume=100, id="", rel_x=0, rel_y=0, rel_z=0
    ):
        try:
            return self.src.play_sound(
                sound,
                looping=looping,
                volume=volume,
                id=id,
                rel_x=rel_x,
                rel_y=rel_y,
                rel_z=rel_z,
            )
        except Exception as e:
            pass

    def on_hit(self, object, hp):
        pass

    def on_interact(self, object):
        pass

    def loop(self):
        pass

    def destroy(self):
        self.src.destroy()
