# imports for the engine
from direct.showbase.ShowBase import ShowBase

from ClientRepository import GameClientRepository
from direct.gui.DirectGui import *
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from panda3d.core import TextNode, WindowProperties, Vec3, DirectionalLight
from Camera import Camera

GRAVITY = Vec3(0, 0, -9.81)


class GameClient(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.camera_mgr: Camera | None = None

        properties = WindowProperties()
        properties.set_size(1280, 720)
        properties.set_title("Game")
        self.win.request_properties(properties)

        self.disable_mouse()
        self.render.set_shader_auto()

        self.camera.set_pos(0, -10, 5)

        d_light = DirectionalLight('dlight')
        d_light.set_color((0.5, 0.8, 0.8, 1))
        dlnp = self.render.attach_new_node(d_light)
        dlnp.set_hpr(0, -60, 0)
        self.render.set_light(dlnp)

        self.accept("client-ready", self.set_connected_message)

        self.title = self.add_title("Panda3D: Tutorial - Distributed Network (NOT CONNECTED)")

        self.cr = GameClientRepository(self)

        self.main_menu_backdrop = DirectFrame(frameColor=(0, 0, 0, 1),
                                              frameSize=(-1, 1, -1, 1),
                                              parent=self.render2d)
        self.main_menu = DirectFrame(frameColor=(1, 1, 1, 0))
        title1 = DirectLabel(text="PUSSY TIGHT",
                             scale=0.3,
                             pos=(0, 0, 0.7),
                             parent=self.main_menu,
                             relief=None,
                             text_fg=(1, 1, 1, 1))

        btn = DirectButton(text="Join Game",
                           command=self.join,
                           pos=(0, 0, 0.2),
                           parent=self.main_menu,
                           scale=0.1,
                           frameSize=(-4, 4, -1, 1),
                           text_scale=0.75,
                           relief=DGG.FLAT,
                           text_pos=(0, -0.2))
        btn.set_transparency(1)

        self.exitFunc = self.leave

    def join(self):
        self.main_menu.hide()
        self.main_menu_backdrop.hide()
        self.cr.request_join()

        def join_success():
            self.camera_mgr = Camera(self.camera, self.cr.player, 40, 10, 0.75)
            self.cr.player.set_input_space(self.camera)
            self.task_mgr.add(self.update, "update-task")
            self.title["text"] = ("Panda3D: Tutorial - Distributed Network (CONNECTED) | ID = "
                                  + str(self.cr.player.doId))

        self.accept("player-ready", join_success)
        self.accept_once("q", self.leave)

    def leave(self):
        self.task_mgr.remove("update-task")
        self.camera_mgr = None
        self.cr.request_leave()

    def update(self, task):
        """The main task that will handle the client-side game logic"""
        dt = self.clock.get_dt()
        self.cr.update()
        self.camera_mgr.update(dt)
        return Task.cont

    # Function to put instructions on the screen.
    def add_instruction(self, pos, msg):
        return OnscreenText(text=msg, fg=(0, 0, 0, 1), shadow=(1, 1, 1, 1),
                            parent=self.a2dTopLeft, align=TextNode.ALeft,
                            pos=(0.08, -pos - 0.04), scale=0.06)

    # Function to put title on the screen.
    def add_title(self, text):
        return OnscreenText(text=text, pos=(-0.1, 0.09), scale=0.08,
                            parent=self.a2dBottomRight, align=TextNode.ARight,
                            fg=(1, 1, 1, 1), shadow=(0, 0, 0, 1))

    def set_connected_message(self):
        self.title["text"] = "Panda3D: Tutorial - Distributed Network (CONNECTED)"


client = GameClient()
client.run()
