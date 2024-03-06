import random

from direct.distributed.DistributedNode import DistributedNode
from direct.showbase.MessengerGlobal import messenger
from panda3d.bullet import BulletCapsuleShape, Z_up
from Helpers import BulletRigidBodyNP
from Input import global_input


class DPlayer(DistributedNode, BulletRigidBodyNP):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        BulletRigidBodyNP.__init__(self, "Player")
        self.model = base.loader.load_model("models/panda")
        self.model.set_scale(0.2)
        self.model.reparent_to(self)
        # self.setCacheable(True)

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.reparent_to(base.render)

    def delete(self):
        print("deleting player object", self.doId)
        self.detach_node()
        DistributedNode.delete(self)

    def update(self, dt):
        pass

    def d_send_input(self):
        """Converts player input to tuple and sends it to the AI server."""
        move_input = global_input.move_input
        p_input = (int(move_input.get_x()),
                   int(move_input.get_y()),
                   global_input.jump_pressed)
        self.sendUpdate("send_input", [p_input])
