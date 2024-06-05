from direct.showbase import DirectObject
from panda3d.core import Vec2


class Input(DirectObject.DirectObject):
    def __init__(self):
        super().__init__()

        self.d_pad_map = {
            "w": False,
            "s": False,
            "a": False,
            "d": False,
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.jump_pressed = False

        def set_jump_pressed(value):
            self.jump_pressed = value

        self.accept("space", set_jump_pressed, [True])

        self.accept("w", self.update_map, ["w", True])
        self.accept("w-up", self.update_map, ["w", False])
        self.accept("s", self.update_map, ["s", True])
        self.accept("s-up", self.update_map, ["s", False])
        self.accept("a", self.update_map, ["a", True])
        self.accept("a-up", self.update_map, ["a", False])
        self.accept("d", self.update_map, ["d", True])
        self.accept("d-up", self.update_map, ["d", False])

        self.accept("arrow_up", self.update_map, ["up", True])
        self.accept("arrow_up-up", self.update_map, ["up", False])
        self.accept("arrow_down", self.update_map, ["down", True])
        self.accept("arrow_down-up", self.update_map, ["down", False])
        self.accept("arrow_left", self.update_map, ["left", True])
        self.accept("arrow_left-up", self.update_map, ["left", False])
        self.accept("arrow_right", self.update_map, ["right", True])
        self.accept("arrow_right-up", self.update_map, ["right", False])

    def move_input(self):
        move_input = Vec2(0.0, 0.0)
        if self.d_pad_map["w"]:
            move_input.add_y(1.0)
        if self.d_pad_map["s"]:
            move_input.add_y(-1.0)
        if self.d_pad_map["a"]:
            move_input.add_x(-1.0)
        if self.d_pad_map["d"]:
            move_input.add_x(1.0)
        return move_input

    def look_input(self):
        look_input = Vec2(0.0, 0.0)
        if self.d_pad_map["up"]:
            look_input.add_y(1.0)
        if self.d_pad_map["down"]:
            look_input.add_y(-1.0)
        if self.d_pad_map["left"]:
            look_input.add_x(-1.0)
        if self.d_pad_map["right"]:
            look_input.add_x(1.0)
        look_input.normalize()
        return look_input

    def update_map(self, key, value):
        self.d_pad_map[key] = value


global_input = Input()
