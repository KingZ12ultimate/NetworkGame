from direct.distributed.DistributedNode import DistributedNode
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import GeoMipTerrain


class DLevel(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)

        # initiate the terrain
        self.terrain = GeoMipTerrain("LevelTerrain")
        self.terrain.set_heightfield("Assets/Textures/HeightMap.png")

        self.height = 10
        self.height_map = self.terrain.heightfield()
        offset = -self.height_map.get_x_size() * 0.5

        self.terrain.get_root().reparent_to(self)
        self.terrain.get_root().set_sz(self.height)
        self.terrain.get_root().set_pos(offset, offset, -self.height * 0.5)

        # set terrain properties
        self.terrain.set_block_size(64)
        self.terrain.set_near_far(60, 150)
        self.terrain.set_focal_point(base.camera)

    def delete(self):
        print("deleting level", self.doId)
        self.remove_node()
        DistributedNode.delete(self)

    def start_level(self, player_ids):
        print("start level")
        self.terrain.generate()
        texture = base.loader.load_texture("Assets/Textures/grass_texture.jpg")
        self.terrain.get_root().set_texture(texture)
        self.reparent_to(base.render)
        messenger.send("start_level", [player_ids])

    def end_level(self):
        print("end level")
        messenger.send("end_level")
