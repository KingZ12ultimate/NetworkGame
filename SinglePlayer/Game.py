from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import WindowProperties, Vec3, BitMask32
from panda3d.core import AmbientLight

from panda3d.bullet import BulletWorld, BulletRigidBodyNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletDebugNode

from Input import global_input

GRAVITY = Vec3(0, 0, -9.81)
DEBUG = True


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        from Camera import Camera
        from Player import Player

        properties = WindowProperties()
        properties.set_size(1280, 720)
        properties.set_title("Game")
        self.win.request_properties(properties)

        self.disable_mouse()
        self.render.set_shader_auto()

        if DEBUG:
            self.debug_np = self.render.attach_new_node(BulletDebugNode("Debug"))
            self.debug_np.node().show_wireframe(True)
            self.debug_np.node().show_bounding_boxes(False)
            self.debug_np.node().show_normals(False)
            self.debug_np.show()
            global_input.subscribe_to_event("p", self.toggle_debug)

        # ambient_light = AmbientLight("ambient light")
        # ambient_light.set_color((0.8, 0.8, 0.8, 1))
        # ambient_light_np = self.render.attach_new_node(ambient_light)
        # self.render.set_light(ambient_light_np)

        self.world = BulletWorld()
        self.world.set_gravity(GRAVITY)
        if DEBUG:
            self.world.set_debug_node(self.debug_np.node())

        self.ground_np = self.render.attach_new_node(BulletRigidBodyNode("Ground"))
        ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        self.ground_np.node().add_shape(ground_shape)
        self.world.attach_rigid_body(self.ground_np.node())

        ground_model = self.loader.load_model("Models/floor.glb")
        ground_model.reparent_to(self.ground_np)
        ground_model.set_color(0.8, 0.8, 0.8, 1)

        self.ground_np.set_collide_mask(BitMask32.all_on())

        self.__player = Player("models/panda", Vec3(0, 0, 4),
                               player_input_space=self.camera)
        self.camera_manager = Camera(self.camera, self.__player.rigid_body_np,
                                     40, 10, 0.75)
        self.update_task = self.task_mgr.add(self.update, "update")

    if DEBUG:
        def toggle_debug(self):
            if self.debug_np.is_hidden():
                self.debug_np.show()
            else:
                self.debug_np.hide()

    def update(self, task: Task):
        dt = self.clock.get_dt()
        self.ground_np.node().set_active(True)
        self.__player.update(dt)
        self.world.do_physics(dt)
        self.camera_manager.update(dt)
        # Reset input
        global_input.reset_input()
        return task.cont


game = Game()
game.run()
