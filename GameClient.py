# imports for the engine
from direct.showbase.ShowBase import ShowBase

from Repositories.ClientRepository import GameClientRepository
from GUI.MainMenu import MainMenu
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
        d_light.set_color((0.9, 0.9, 0.9, 1))
        dlnp = self.render.attach_new_node(d_light)
        dlnp.set_hpr(0, -60, 0)
        self.render.set_light(dlnp)

        self.accept("client-ready", self.set_connected_message)

        self.title = self.add_title("Panda3D: Tutorial - Distributed Network (NOT CONNECTED)")
        inst1 = self.add_instruction(0.06, "q: Quit")

        self.cr = GameClientRepository(self)
        self.accept_once("join", self.join)

        self.menu = MainMenu(self.render2d)

    def join(self):
        self.menu.main_menu.hide()
        self.menu.main_menu_backdrop.hide()
        self.cr.request_join()

        def join_success():
            self.camera_mgr = Camera(self.camera, self.cr.player, 40, 10, 0.75)
            self.cr.player.set_input_space(self.camera)
            self.task_mgr.add(self.update, "update-task")
            self.title["text"] = ("Panda3D: Tutorial - Distributed Network (CONNECTED) | ID = "
                                  + str(self.cr.player.doId))

        self.accept("level-ready", join_success)
        self.accept_once("q", self.leave)

    def leave(self):
        """ Leave the current level. """
        self.task_mgr.remove("update-task")
        self.camera_mgr = None
        self.cr.request_leave()

        # bring back the main menu
        self.menu.main_menu_backdrop.show()
        self.menu.main_menu.show()

    def quit(self):
        """ Quit the application. """
        self.cr.quit()

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
