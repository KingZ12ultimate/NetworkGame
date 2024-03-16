from direct.distributed.DistributedNodeAI import DistributedNodeAI
from panda3d.bullet import BulletGhostNode, BulletBoxShape
from panda3d.core import NodePath


class BulletGhostNodeNP(NodePath):
    def __init__(self, name="Ghost"):
        NodePath.__init__(self, BulletGhostNode(name))


class DCherryAI(DistributedNodeAI, BulletGhostNodeNP):
    COUNT = 0

    def __init__(self, air):
        self.COUNT += 1
        DistributedNodeAI.__init__(self, air)
        BulletGhostNodeNP.__init__(self, "Cherry" + str(self.COUNT))

        self.model = base.loader.load_model("models/frowney")
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        self.node().add_shape(BulletBoxShape(size))

