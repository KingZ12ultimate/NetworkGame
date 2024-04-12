from direct.distributed.DistributedNodeAI import DistributedNodeAI
from panda3d.core import Filename, PNMImage, NodePath, Vec3
from panda3d.bullet import BulletWorld
from Globals import BulletRigidBodyNP, masks, GRAVITY
from DistributedObjects.DCherryAI import DCherryAI


class DLevelAI(DistributedNodeAI, BulletRigidBodyNP):
    SIZE = 1024
    NUM_CHERRIES_PER_ROW = 20

    def __init__(self, air, max_players, level_zone):
        DistributedNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Terrain")

        self.max_players = max_players
        self.players = []
        self.level_zone = level_zone

        self.world = BulletWorld()
        self.world.set_gravity(GRAVITY)
        self.world_np = NodePath("Physics-World")  # the root node of the level's physics world

        self.set_collide_mask(masks["terrain"])
        self.cherries: list[DCherryAI] = []

        self.height_map = PNMImage(Filename("Assets/HeightMap.png"))
        self.height = 10

    def delete(self):
        self.players = []
        DistributedNodeAI.delete(self)

    def can_join(self):
        return len(self.players) < self.max_players

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
                self.players.remove(p)
                self.world.remove(p.node())
                self.air.sendDeleteMsg(player_id)

    def generate_cherries(self):
        cell_size = self.SIZE / self.NUM_CHERRIES_PER_ROW
        offset = -512
        for y in range(self.NUM_CHERRIES_PER_ROW):
            for x in range(self.NUM_CHERRIES_PER_ROW):
                xy = (cell_size * (0.5 + x), cell_size * (0.5 + y))
                pos = (offset + xy[0],
                       offset + xy[1],
                       (self.height_map.get_gray(round(xy[0]), round(xy[1]))) * self.height + 5)
                cherry = DCherryAI(self.air, self, pos)
                self.cherries.append(cherry)
                self.air.createDistributedObject(distObj=cherry, zoneId=self.zoneId)

    def update(self):
        for cherry in self.cherries:
            cherry.update()
