import math

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from panda3d.core import Filename, PNMImage, NodePath, Vec3
from panda3d.bullet import BulletWorld, BulletPlaneShape, BulletHeightfieldShape, Z_up
from Globals import BulletRigidBodyNP, GRAVITY, CHERRIES_TO_WIN, masks
from DistributedObjects.DCherryAI import DCherryAI


basedir = ""


class DLevelAI(DistributedNodeAI):
    SIZE = 1024
    NUM_CHERRIES_PER_ROW = 20

    def __init__(self, air, max_players):
        DistributedNodeAI.__init__(self, air)

        # level properties
        self.max_players = max_players
        self.players = []
        self.player_models = {
            "Assets/Models/Doozy.glb": False,
            "Assets/Models/Mousey.glb": False,
            "Assets/Models/Claire.glb": False,
            "Assets/Models/AJ.glb": False
        }

        # physics
        self.world = BulletWorld()
        self.world.set_gravity(GRAVITY)
        self.world_np = NodePath("Physics-World")  # the root node of the level's physics world

        self.cherries: list[DCherryAI] = []

        # terrain properties
        self.height = 10
        self.height_map = PNMImage(Filename(basedir + "Assets/Textures/HeightMap.png"))
        self.terrain_rigidbody_np = BulletRigidBodyNP("Terrain")

        collider = BulletHeightfieldShape(self.height_map, self.height, Z_up)
        self.terrain_rigidbody_np.node().add_shape(collider)
        self.terrain_rigidbody_np.set_collide_mask(masks["terrain"])
        self.world.attach(self.terrain_rigidbody_np.node())

        # world boundaries as plane colliders
        bounds = []
        offset = self.height_map.get_x_size() * 0.5

        boundary = BulletPlaneShape(Vec3(-1, 0, 0), -offset)
        boundary_np = BulletRigidBodyNP("Boundary_0")
        boundary_np.node().add_shape(boundary)
        boundary_np.set_collide_mask(masks["terrain"])
        self.world.attach(boundary_np.node())
        bounds.append(boundary_np)

        boundary = BulletPlaneShape(Vec3(0, -1, 0), -offset)
        boundary_np = BulletRigidBodyNP("Boundary_1")
        boundary_np.node().add_shape(boundary)
        boundary_np.set_collide_mask(masks["terrain"])
        self.world.attach(boundary_np.node())
        bounds.append(boundary_np)

        boundary = BulletPlaneShape(Vec3(1, 0, 0), -offset)
        boundary_np = BulletRigidBodyNP("Boundary_2")
        boundary_np.node().add_shape(boundary)
        boundary_np.set_collide_mask(masks["terrain"])
        self.world.attach(boundary_np.node())
        bounds.append(boundary_np)

        boundary = BulletPlaneShape(Vec3(0, 1, 0), -offset)
        boundary_np = BulletRigidBodyNP("Boundary_3")
        boundary_np.node().add_shape(boundary)
        boundary_np.set_collide_mask(masks["terrain"])
        self.world.attach(boundary_np.node())
        bounds.append(boundary_np)

        base.task_mgr.add(self.can_start, "can-start-level")
        self.update_task = None
        self.is_running = False

    def delete(self):
        if self.update_task is not None:
            self.update_task.remove()

        self.air.level_zone_allocator.free(self.zoneId)

        for player in self.players:
            self.air.sendDeleteMsg(player.doId)
        self.players = []

        for cherry in self.cherries:
            self.air.sendDeleteMsg(cherry.doId)
        self.cherries = []

        DistributedNodeAI.delete(self)

    def can_join(self):
        """Returns whether players can still join the level"""
        return len(self.players) < self.max_players and not self.is_running

    def can_start(self, task):
        if self.can_join():
            return task.cont
        for player in self.players:
            if not player.ready:
                return task.cont
        self.d_start_level()
        return task.done

    def add_player(self, player):
        # Adding a collider
        player.add_collider()

        # Setting physical attributes
        player.node().set_mass(1.0)
        player.node().set_angular_factor(Vec3(0, 0, 1.0))

        # Setting up CCD
        player.node().set_ccd_motion_threshold(1e-07)
        player.node().set_ccd_swept_sphere_radius(0.5)

        # Attaching the player to the world
        self.world.attach(player.node())
        player.reparent_to(self.world_np)
        self.players.append(player)

    def remove_player(self, player_id):
        for p in self.players:
            if p.doId == player_id:
                self.player_models[p.model_path] = False
                self.players.remove(p)
                self.world.remove(p.node())
                self.air.sendDeleteMsg(player_id)

    def d_start_level(self):
        self.is_running = True
        ids = []
        for player in self.players:
            player.d_set_model()
            ids.append(player.doId)
        self.generate_cherries(cherry_height=4)
        self.update_task = base.task_mgr.add(
            self.update,
            "level-update-" + str(self.doId)
        )
        self.sendUpdate("start_level", [ids])

    def d_end_level(self):
        self.sendUpdate("end_level")

    def update(self, task):
        # Once a player collected enough cherries, end the level
        dt = base.clock.get_dt()

        for player in self.players:
            if player.score >= CHERRIES_TO_WIN:
                self.d_end_level()
                return task.done
            player.update(dt)

        for cherry in self.cherries:
            cherry.update()

        self.world.do_physics(dt)

        for player in self.players:
            pos = player.get_pos()
            player.d_setPos(pos.get_x(), pos.get_y(), pos.get_z())

        return task.cont

    def generate_cherries(self, cherry_height):
        cell_size = self.SIZE / self.NUM_CHERRIES_PER_ROW
        size = self.height_map.get_size()
        offset = -size.get_x() * 0.5
        for y in range(self.NUM_CHERRIES_PER_ROW):
            for x in range(self.NUM_CHERRIES_PER_ROW):
                cx = cell_size * (0.5 + x)
                cy = cell_size * (0.5 + y)
                cz = self.height_map.get_gray(
                    math.floor(cx),
                    size.get_y() - math.floor(cy)
                )
                cx += offset
                cy += offset
                cz = (cz - 0.5) * self.height + cherry_height
                cherry = DCherryAI(self.air, self, (cx, cy, cz))
                self.cherries.append(cherry)
                self.air.createDistributedObject(distObj=cherry, zoneId=self.zoneId)

    def remove_cherry(self, cherry_id):
        for c in self.cherries:
            if c.doId == cherry_id:
                self.cherries.remove(c)
                self.world.remove(c.node())
