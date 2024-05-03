from direct.distributed.DistributedNode import DistributedNode
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import GeoMipTerrain, PNMImage, Filename


class DLevel(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)

        # initiate the terrain
        self.terrain = GeoMipTerrain("LevelTerrain")
        self.terrain.set_heightfield("Assets/HeightMap.png")

        self.height = 10
        self.height_map = self.terrain.heightfield()
        offset = -self.height_map.get_x_size() * 0.5

        self.terrain.get_root().reparent_to(self)
        self.terrain.get_root().set_sz(self.height)
        self.terrain.get_root().set_pos(offset, offset, -self.height * 0.5)

        # set terrain properties
        self.terrain.set_block_size(64)
        self.terrain.set_near_far(40, 100)
        self.terrain.set_focal_point(base.camera)

    def delete(self):
        print("deleting level", self.doId)
        self.detach_node()
        DistributedNode.delete(self)

    def start_level(self):
        print("start level")
        self.terrain.generate()
        self.reparent_to(base.render)
        messenger.send("start-level")

    def d_generate_cherries(self):
        self.sendUpdate("generate_cherries")
