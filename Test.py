import simplepbr

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from panda3d.core import UniqueIdAllocator


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disable_mouse()
        self.render.set_shader_auto()

        simplepbr.init()

        self.camera.set_pos(0, -10, 10)
        self.player = Actor("Assets/Doozy.glb")
        self.player.reparent_to(self.render)

        self.map = {
            "up": False,
            "down": False,
            "left": False,
            "right": False,
        }

        self.accept("w", self.update_map, ["up", True])
        self.accept("w-up", self.update_map, ["up", False])
        self.accept("s", self.update_map, ["down", True])
        self.accept("s-up", self.update_map, ["down", False])
        self.accept("a", self.update_map, ["left", True])
        self.accept("a-up", self.update_map, ["left", False])
        self.accept("d", self.update_map, ["right", True])
        self.accept("d-up", self.update_map, ["right", False])

        self.task_mgr.add(self.update)

        self.allocator = UniqueIdAllocator(1000, 1200)
        for i in range(200):
            print(self.allocator.allocate(), end=', ')
        print()
        for i in range(1000, 1100):
            self.allocator.free(i)

            print(self.allocator.allocate(), end=', ')

    def update_map(self, key, value):
        self.map[key] = value

    def update(self, task):
        pos = self.player.get_pos()
        if self.map["up"]:
            pos.add_y(1)
        if self.map["down"]:
            pos.add_y(-1)
        if self.map["left"]:
            pos.add_x(-1)
        if self.map["right"]:
            pos.add_x(1)
        self.player.set_pos(pos)
        self.camera.look_at(self.player)
        return task.cont


game = Game()
game.run()
