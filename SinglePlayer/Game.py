import simplepbr, math

from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import WindowProperties, Vec3, DirectionalLight, Filename, PNMImage, GeoMipTerrain, BitMask32

from panda3d.bullet import BulletWorld, BulletHeightfieldShape, Z_up
from panda3d.bullet import BulletDebugNode, BulletRigidBodyNode

from Input import global_input
from Ghost import Ghost

GRAVITY = Vec3(0, 0, -9.81)
DEBUG = True


class Game(ShowBase):
    SIZE = 1024
    NUM_CHERRIES_PER_ROW = 20

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

        simplepbr.init()

        d_light = DirectionalLight('d_light')
        d_light.set_color((0.9, 0.9, 0.9, 1))
        dlnp = self.render.attach_new_node(d_light)
        dlnp.set_hpr(0, -60, 0)
        self.render.set_light(dlnp)

        if DEBUG:
            self.debug_np = self.render.attach_new_node(BulletDebugNode("Debug"))
            self.debug_np.node().show_wireframe(True)
            self.debug_np.node().show_bounding_boxes(False)
            self.debug_np.node().show_normals(False)
            self.debug_np.hide()
            global_input.subscribe_to_event("p", self.toggle_debug)

        path = "/c/Users/roee/PycharmProjects/NetworkGame/Assets/HeightMap.png"
        self.height = 10
        self.height_map = PNMImage(Filename(path))

        self.world = BulletWorld()
        self.world.set_gravity(GRAVITY)
        if DEBUG:
            self.world.set_debug_node(self.debug_np.node())

        # initiate the terrain
        self.terrain = GeoMipTerrain("LevelTerrain")
        self.terrain.set_heightfield(path)
        self.terrain.get_root().reparent_to(self.render)
        self.terrain.get_root().set_sz(self.height)
        self.terrain.get_root().set_pos(-512, -512, -5)

        # set terrain properties
        self.terrain.set_block_size(64)
        self.terrain.set_near_far(40, 100)
        self.terrain.set_focal_point(self.camera)
        self.terrain.generate()

        self.terrain_rigidbody_np = self.render.attach_new_node(BulletRigidBodyNode("Terrain"))
        self.terrain_rigidbody_np.set_collide_mask(BitMask32.bit(0))
        collider = BulletHeightfieldShape(self.height_map, self.height, Z_up)
        self.terrain_rigidbody_np.node().add_shape(collider)
        self.world.attach(self.terrain_rigidbody_np.node())

        self.__player = Player("models/panda", Vec3(0, 0, 4),
                               player_input_space=self.camera)
        self.camera_manager = Camera(self.camera, self.__player.rigid_body_np,
                                     40, 10, 0.75)
        self.update_task = self.task_mgr.add(self.update, "update")

        cell_size = self.SIZE / self.NUM_CHERRIES_PER_ROW
        offset = -512
        for y in range(self.NUM_CHERRIES_PER_ROW):
            for x in range(self.NUM_CHERRIES_PER_ROW):
                xy = (cell_size * (0.5 + x), cell_size * (0.5 + y))
                pos = (offset + xy[0],
                       offset + xy[1],
                       self.height_map.get_gray(math.floor(xy[0]),
                                                self.height_map.get_y_size() - math.floor(xy[1])) *
                       self.height - 5)
                ghost = Ghost()
                ghost.ghost_np.set_pos(pos)

    if DEBUG:
        def toggle_debug(self):
            if self.debug_np.is_hidden():
                self.debug_np.show()
            else:
                self.debug_np.hide()

    def update(self, task: Task):
        dt = self.clock.get_dt()
        self.terrain_rigidbody_np.node().set_active(True)
        self.__player.update(dt)
        self.world.do_physics(dt)
        self.camera_manager.update(dt)
        self.terrain.update()
        # Reset input
        global_input.reset_input()
        return task.cont


game = Game()
game.run()
