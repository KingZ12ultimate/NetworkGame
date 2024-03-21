from direct.distributed.DistributedNodeAI import DistributedNodeAI
from panda3d.core import Filename, PNMImage
from Globals import BulletRigidBodyNP, masks
from DCherryAI import DCherryAI


class DLevelAI(DistributedNodeAI, BulletRigidBodyNP):
    SIZE = 1024
    NUM_CHERRIES_PER_ROW = 20

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Terrain")

        self.set_collide_mask(masks["terrain"])
        self.cherries: list[DCherryAI] = []

        self.height_map = PNMImage(Filename("HeightMap.png"))
        self.height = 10

    def generate_cherries(self):
        cell_size = self.SIZE / self.NUM_CHERRIES_PER_ROW
        offset = -512
        for y in range(self.NUM_CHERRIES_PER_ROW):
            for x in range(self.NUM_CHERRIES_PER_ROW):
                xy = (cell_size * (0.5 + x), cell_size * (0.5 + y))
                pos = (offset + xy[0],
                       offset + xy[1],
                       (self.height_map.get_gray(round(xy[0]), round(xy[1])) - 0.5) * self.height)
                cherry = DCherryAI(self.air, pos)
                self.cherries.append(cherry)
                self.air.createDistributedObject(distObj=cherry, zoneId=self.zoneId)
