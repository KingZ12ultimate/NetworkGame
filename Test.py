import itertools

import simplepbr

from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TextNode, ConfigVariableString


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.disable_mouse()
        self.render.set_shader_auto()

        print(ConfigVariableString("server-host"))

        simplepbr.init()

        self.camera.set_pos(0, -10, 10)
        self.player = Actor("Assets/Models/Doozy.glb")
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

        player_ids = [1, 2, 3, 4]
        score_text = {}
        for i, id in enumerate(player_ids):
            score_text[id] = OnscreenText(text="Player {}: {}".format(id, 0),
                                          parent=self.a2dTopLeft,
                                          pos=(0, -0.08 - i * 0.1),
                                          align=TextNode.ALeft)

        self.button_images = (
            self.loader.load_texture("UI/UIButton.png"),
            self.loader.load_texture("UI/UIButtonPressed.png"),
            self.loader.load_texture("UI/UIButtonHighlighted.png"),
            self.loader.load_texture("UI/UIButtonDisabled.png")
        )

        self.dialog = DirectDialog(frameSize=(-0.8, 0.8, -0.7, 0.7),
                                   fadeScreen=0.4,
                                   relief=DGG.FLAT,
                                   frameTexture="UI/stoneFrame.png")

        title = DirectLabel(text="Instructions",
                            parent=self.dialog,
                            scale=0.2,
                            pos=(0, 0, 0.47),
                            relief=None)

        self.instructions = [
            self.add_instruction(0, "Use arrow keys to move the camera"),
            self.add_instruction(0.1, "Use \"space\" key to jump"),
            self.add_instruction(0.2, "Use \"WASD\" keys to move"),
            self.add_instruction(0.3, "Be the first to grab {} cherries!".format(30))
        ]

        btn = DirectButton(text="OK!",
                           command=self.dialog.hide,
                           pos=(0, 0, -0.4),
                           parent=self.dialog,
                           scale=0.1,
                           frameSize=(-2, 2, -1, 1),
                           frameTexture=self.button_images,
                           text_scale=0.75,
                           relief=DGG.GROOVE,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

    def add_instruction(self, pos, msg):
        return DirectLabel(text=msg,
                           parent=self.dialog,
                           scale=0.08,
                           pos=(0, 0, 0.35 - pos),
                           relief=None)

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
