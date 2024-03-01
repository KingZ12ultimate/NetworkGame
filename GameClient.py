# imports for the engine
from direct.showbase.ShowBase import ShowBase

# imports for physics
from panda3d.bullet import BulletWorld, BulletRigidBodyNode

from ClientRepository import GameClientRepository
from direct.gui.OnscreenText import OnscreenText
from direct.task.Task import Task
from panda3d.core import TextNode, WindowProperties, PandaNode
from Camera import Camera


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

        self.exitFunc = self.request_leave
        self.accept("client-ready", self.set_connected_message)

        self.title = self.add_title("Panda3D: Tutorial - Distributed Network (NOT CONNECTED)")
        inst1 = self.add_instruction(0.06, "esc: Close the client")
        inst2 = self.add_instruction(0.12, "See console output")

        self.cr = GameClientRepository()
        self.accept_once("t", self.request_join)
        self.accept_once("player-created", self.setup_camera)

    def request_join(self):
        self.cr.request_join()
        self.accept_once("join-success", self.join_success)

    def join_success(self):
        self.title["text"] = ("Panda3D: Tutorial - Distributed Network (CONNECTED) | ID = "
                              + str(self.cr.player.doId))
        self.messenger.send("player-created")

    def request_leave(self):
        self.task_mgr.remove("update-task")
        self.camera_mgr = None
        self.cr.request_leave()

    def setup_camera(self):
        self.camera_mgr = Camera(self.camera, self.cr.player, 40, 10, 0.75)
        self.task_mgr.add(self.update, "update-task")

    def update(self, task):
        """The main task that will handle the client-side game logic"""
        dt = self.clock.get_dt()
        self.camera_mgr.update(dt)
        self.cr
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
