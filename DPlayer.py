from direct.distributed.DistributedNode import DistributedNode
from panda3d.core import Vec3
from Helpers import BulletRigidBodyNP
from Input import global_input


class DPlayer(DistributedNode, BulletRigidBodyNP):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        BulletRigidBodyNP.__init__(self, "Player")
        self.model = base.loader.load_model("models/panda")
        self.model.set_scale(0.2)
        self.model.reparent_to(self)
        self.input_space = base.render
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

    def set_input_space(self, input_space):
        self.input_space = input_space

    def get_relative_input(self):
        if self.input_space:
            forward = self.input_space.get_quat().get_forward()
            forward.set_z(0)
            forward.normalize()
            right = self.input_space.get_quat().get_right()
            right.set_z(0)
            right.normalize()
            move_input = global_input.move_input
            return right * move_input.get_x() + forward * move_input.get_y()
        else:
            return Vec3(global_input.move_input, 0)

    def d_send_input(self):
        """Converts player input to tuple and sends it to the AI server."""
        move_input = self.get_relative_input()
        p_input = (move_input.get_x(),
                   move_input.get_y(),
                   move_input.get_z(),
                   global_input.jump_pressed)
        self.sendUpdate("send_input", [p_input])
