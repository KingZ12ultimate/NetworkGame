from direct.distributed.DistributedNode import DistributedNode
from direct.interval.LerpInterval import LerpQuatInterval
from panda3d.core import Vec3, NodePath, Quat
from Globals import BulletRigidBodyNP
from Input import global_input
from math import atan2, sin, cos


class DPlayer(DistributedNode, BulletRigidBodyNP):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        BulletRigidBodyNP.__init__(self, "Player")

        self.model = base.loader.load_model("models/panda")
        self.model.set_scale(0.2)
        self.set_h(180)
        self.model.reparent_to(self)
        self.input_space: NodePath = base.render
        # self.setCacheable(True)

        self.move_input = Vec3(0, 0, 0)
        self.rotation_duration = 0.2
        self.rotation_interval = None

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.reparent_to(base.render)

    def delete(self):
        print("deleting player object", self.doId)
        self.detach_node()
        DistributedNode.delete(self)

    def handle_rotation(self):
        if self.rotation_interval is not None:
            if self.rotation_interval.is_playing():
                return

        if self.move_input != 0:
            angle = atan2(self.move_input.get_x(), self.move_input.get_y())
            target_rotation = Quat(cos(angle / 2.0), 0, 0, -sin(angle / 2.0))
            self.rotation_interval = LerpQuatInterval(nodePath=self.model,
                                                      duration=self.rotation_duration,
                                                      quat=target_rotation,
                                                      blendType="easeInOut",
                                                      name="rotationInterval")
            self.rotation_interval.start()

        # send hpr to all clients
        hpr = self.model.get_hpr()
        self.d_set_model_hpr(hpr.get_x(), hpr.get_y(), hpr.get_z())

    def update(self):
        self.move_input = self.get_relative_input()
        self.handle_rotation()

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
            res = right * move_input.get_x() + forward * move_input.get_y()
        else:
            res = Vec3(global_input.move_input, 0)
        res.normalize()
        return res

    def get_model_hpr(self):
        return self.model.get_h(), self.model.get_p(), self.model.get_r()

    def set_model_hpr(self, h, p, r):
        self.model.set_hpr(h, p, r)

    def d_set_model_hpr(self, h, p, r):
        self.sendUpdate("set_model_hpr", [h, p, r])

    def d_send_input(self):
        """Converts player input to tuple and sends it to the AI server."""
        p_input = (self.move_input.get_x(),
                   self.move_input.get_y(),
                   self.move_input.get_z(),
                   global_input.jump_pressed)
        self.sendUpdate("send_input", [p_input])

        # Reset jump input if True
        if p_input[3]:
            global_input.set_jump_pressed(False)
