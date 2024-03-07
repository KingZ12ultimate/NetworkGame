from direct.showbase import DirectObject
from direct.task.Task import Task
from panda3d.core import Vec2


class Input(DirectObject.DirectObject):
    def __init__(self):
        super().__init__()

        self.__d_pad_map = {
            "w": False,
            "s": False,
            "a": False,
            "d": False,
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.__move_input = Vec2(0.0, 0.0)
        self.__look_input = Vec2(0.0, 0.0)
        self.__jump_pressed = False

        self.accept("w", self.__update_map, ["w", True])
        self.accept("w-up", self.__update_map, ["w", False])
        self.accept("s", self.__update_map, ["s", True])
        self.accept("s-up", self.__update_map, ["s", False])
        self.accept("a", self.__update_map, ["a", True])
        self.accept("a-up", self.__update_map, ["a", False])
        self.accept("d", self.__update_map, ["d", True])
        self.accept("d-up", self.__update_map, ["d", False])

        self.accept("space", Input.jump_pressed.setter, [True])

        self.accept("arrow_up", self.__update_map, ["up", True])
        self.accept("arrow_up-up", self.__update_map, ["up", False])
        self.accept("arrow_down", self.__update_map, ["down", True])
        self.accept("arrow_down-up", self.__update_map, ["down", False])
        self.accept("arrow_left", self.__update_map, ["left", True])
        self.accept("arrow_left-up", self.__update_map, ["left", False])
        self.accept("arrow_right", self.__update_map, ["right", True])
        self.accept("arrow_right-up", self.__update_map, ["right", False])

    @property
    def move_input(self):
        self.__move_input = Vec2(0.0, 0.0)
        if self.__d_pad_map["w"]:
            self.__move_input.add_y(1.0)
        if self.__d_pad_map["s"]:
            self.__move_input.add_y(-1.0)
        if self.__d_pad_map["a"]:
            self.__move_input.add_x(-1.0)
        if self.__d_pad_map["d"]:
            self.__move_input.add_x(1.0)
        return self.__move_input

    @property
    def look_input(self):
        self.__look_input = Vec2(0.0, 0.0)
        if self.__d_pad_map["up"]:
            self.__look_input.add_y(1.0)
        if self.__d_pad_map["down"]:
            self.__look_input.add_y(-1.0)
        if self.__d_pad_map["left"]:
            self.__look_input.add_x(-1.0)
        if self.__d_pad_map["right"]:
            self.__look_input.add_x(1.0)
        self.__look_input.normalize()
        return self.__look_input

    @property
    def jump_pressed(self):
        return self.__jump_pressed

    @jump_pressed.setter
    def jump_pressed(self, value):
        self.__jump_pressed = value

    def __update_map(self, key, value):
        self.__d_pad_map[key] = value

    def reset_input(self):
        self.__move_input = Vec2(0.0, 0.0)
        self.__look_input = Vec2(0.0, 0.0)

    def subscribe_to_event(self, event: str, method):
        self.accept(event, method)


global_input = Input()
