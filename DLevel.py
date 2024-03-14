from direct.distributed.DistributedNode import DistributedNode
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import GeoMipTerrain


class DLevel(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)

        # initiate the terrain
        self.terrain = GeoMipTerrain("LevelTerrain")
        self.terrain.set_heightfield("HeightMap.png")
        self.terrain.get_root().reparent_to(self)
        self.terrain.get_root().set_sz(10)
        self.terrain.get_root().set_pos(-512, -512, -5)

        # set terrain properties
        self.terrain.set_block_size(64)
        self.terrain.set_near_far(40, 100)
        self.terrain.set_focal_point(base.camera)

    def announceGenerate(self):
        messenger.send(self.cr.uniqueName("LevelGenerated"), [self.doId])
        DistributedNode.announceGenerate(self)
        self.terrain.generate()
        self.reparent_to(base.render)

    def delete(self):
        print("deleting level", self.doId)
        self.detach_node()
        DistributedNode.delete(self)
