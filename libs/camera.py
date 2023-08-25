from . import audio, consts, movement, options
from .speech import speak


class Camera:
    def __init__(self, game):
        self.game = game
        self.reverb = None
        self.src = audio.Src(False)
        self.focus_object = None
        self.currentzone = ""
        self.x = 0.0
        self.y = 0.0
        self.z = 0.0

    def set_focus_object(self, target):
        if self.focus_object:
            if self.focus_object.on_move == self.move:
                self.focus_object.on_move = None
            if self.focus_object.on_turn == self.turn:
                self.focus_object.on_turn = None
        self.focus_object = target
        target.on_move = self.move
        target.on_turn = self.turn
        self.move(target.x, target.y, target.z)
        self.turn(target.hfacing, target.vfacing, target.bfacing)

    def move(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z
        audio.move(self.x, self.y, self.z)
        self.src.move(self.x, self.y, self.z)

    def turn(self, hdeg, vdeg, bdeg=0):
        audio.turn(hdeg, vdeg, bdeg)
