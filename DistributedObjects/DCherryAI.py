from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.showbase.MessengerGlobal import messenger
from panda3d.bullet import BulletGhostNode, BulletSphereShape
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
        self.model = base.loader.load_model("Assets/Models/cherries.glb")
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = max(size.get_x(), size.get_y(), size.get_z()) * 0.5
        self.node().add_shape(BulletSphereShape(radius))

        self.reparent_to(self.level.world_np)
        self.set_collide_mask(masks["cherry"])
        self.level.world.attach(self.node())
        self.set_pos(pos)

        self.value = 1

    def delete(self):
        self.remove_node()
        DistributedNodeAI.delete(self)

    def update(self):
        if self.node().get_num_overlapping_nodes() > 0:
            for node in self.node().get_overlapping_nodes():
                if "Player" in node.get_name():
                    do_id = int(node.get_name().split("-")[1])
                    player = self.air.doId2do[do_id]
                    player.d_add_score(self.value)
                    player.d_play_sound("pickup")
                    self.level.remove_cherry(self.doId)
                    self.air.sendDeleteMsg(self.doId)

    def request_pos(self):
        self.d_setPos(self.get_x(), self.get_y(), self.get_z())
