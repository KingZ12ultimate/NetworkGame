from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import WindowProperties
from panda3d.core import Vec3, Vec4

from panda3d.bullet import BulletWorld, BulletRigidBodyNode
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletDebugNode

from Input import global_input

GRAVITY = Vec3(0, 0, -9.81)


class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        from Player import Player

        properties = WindowProperties()
        properties.set_size(1280, 720)
        properties.set_title("Pussy Tight")
        self.win.request_properties(properties)

        self.disable_mouse()
        self.render.set_shader_auto()
        self.camera.set_pos(0, -25, 5)

        debug_node = BulletDebugNode("Debug")
        debug_node.show_wireframe(True)
        debug_node.show_bounding_boxes(False)
        debug_node.show_normals(False)
        debug_node_path = self.render.attach_new_node(debug_node)
        debug_node_path.show()

        self.world = BulletWorld()
        self.world.set_gravity(GRAVITY)
        self.world.set_debug_node(debug_node)

        ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        ground_node = BulletRigidBodyNode("Ground")
        ground_node.add_shape(ground_shape)
        ground_node_path = self.render.attach_new_node(ground_node)
        ground_model = self.loader.load_model("Models/floor.glb")
        ground_model.reparent_to(ground_node_path)
        ground_model.set_color(0.8, 0.8, 0.8, 1)
        self.world.attach_rigid_body(ground_node)

        self.__player = Player("models/panda", Vec3(0, 0, 4))
        self.update_task = self.task_mgr.add(self.update, "update")

    def update(self, task: Task):
        dt = self.clock.get_dt()
        self.world.do_physics(dt)
        self.__player.update(dt)

        # Reset input
        global_input.reset_input()
        return task.cont


game = Game()
game.run()
