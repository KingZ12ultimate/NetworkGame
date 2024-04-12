from direct.distributed.DistributedNodeAI import DistributedNodeAI
from panda3d.bullet import BulletGhostNode, BulletBoxShape
from panda3d.core import NodePath
from Globals import masks


class BulletGhostNodeNP(NodePath):
    def __init__(self, name="Ghost"):
        NodePath.__init__(self, BulletGhostNode(name))


class DCherryAI(DistributedNodeAI, BulletGhostNodeNP):
    COUNT = 0

    def __init__(self, air, level, pos=(0, 0, 0)):
        self.COUNT += 1
        DistributedNodeAI.__init__(self, air)
        BulletGhostNodeNP.__init__(self, "Cherry" + str(self.COUNT))

        self.level = level
        self.model = base.loader.load_model("models/frowney")
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        self.node().add_shape(BulletBoxShape(size))

        self.reparent_to(self.air.world_np)
        self.air.world.attach(self.node())
        self.set_collide_mask(masks["player"])
        self.set_pos(pos)

    def announceGenerate(self):
        DistributedNodeAI.announceGenerate(self)

    def update(self):
        if self.node().get_num_overlapping_nodes() > 0:
            for node in self.node().get_overlapping_nodes():
                if node.get_name() == "Player":
                    self.level.cherries.remove(self)
                    self.air.sendDeleteMsg(self.doId)

    def request_pos(self):
        self.d_setPos(self.get_x(), self.get_y(), self.get_z())
