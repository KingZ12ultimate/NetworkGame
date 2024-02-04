from direct.showbase import DirectObject
from direct.task.Task import Task
from panda3d.core import Vec2


class Input(DirectObject.DirectObject):
    def __init__(self):
        super().__init__()

        self.__d_pad_map = {
            "up": False,
            "down": False,
            "left": False,
            "right": False
        }
        self.__move_input = Vec2(0.0, 0.0)
        self.__jump_pressed = False

        self.accept("w", self.__update_map, ["up", True])
        self.accept("w-up", self.__update_map, ["up", False])
        self.accept("s", self.__update_map, ["down", True])
        self.accept("s-up", self.__update_map, ["down", False])
        self.accept("a", self.__update_map, ["left", True])
        self.accept("a-up", self.__update_map, ["left", False])
        self.accept("d", self.__update_map, ["right", True])
        self.accept("d-up", self.__update_map, ["right", False])
        self.accept("space", Input.jump_pressed.setter, [self, True])

    @property
    def move_input(self):
        self.__move_input = Vec2(0.0, 0.0)
        if self.__d_pad_map["up"]:
            self.__move_input.add_y(1.0)
        if self.__d_pad_map["down"]:
            self.__move_input.add_y(-1.0)
        if self.__d_pad_map["left"]:
            self.__move_input.add_x(-1.0)
        if self.__d_pad_map["right"]:
            self.__move_input.add_x(1.0)
        return self.__move_input

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

    def subscribe_to_event(self, event: str, method):
        self.accept(event, method)


global_input = Input()
