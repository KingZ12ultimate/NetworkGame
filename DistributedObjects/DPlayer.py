from direct.interval.LerpInterval import LerpQuatInterval
from direct.showbase.MessengerGlobal import messenger
from DistributedObjects.DActor import DActor
from panda3d.core import Vec3, NodePath, Quat
from Input import global_input
from Globals import player_model_scale
from math import atan2, sin, cos


class DPlayer(DActor):
    def __init__(self, cr):
        DActor.__init__(self, cr)

        self.input_space: NodePath = base.render
        self.move_input = Vec3(0, 0, 0)
        self.rotation_duration = 0.2
        self.rotation_interval = None

        self.score = 0

    def announceGenerate(self):
        DActor.announceGenerate(self)
        self.reparent_to(base.render)
        messenger.send("player_joined")
        print("Player generated")

    def delete(self):
        print("deleting player object", self.doId)
        DActor.delete(self)

    # region Rotation
    def handle_rotation(self):
        if self.rotation_interval is not None:
            if self.rotation_interval.is_playing():
                return

        if self.move_input != 0:
            move = -self.move_input
            angle = atan2(move.get_x(), move.get_y())
            target_rotation = Quat(cos(angle / 2.0), 0, 0, -sin(angle / 2.0))
            self.rotation_interval = LerpQuatInterval(nodePath=self.actor,
                                                      duration=self.rotation_duration,
                                                      quat=target_rotation,
                                                      blendType="easeInOut",
                                                      name="rotationInterval")
            self.rotation_interval.start()

        # send hpr to all clients
        hpr = self.actor.get_hpr()
        self.d_set_model_hpr(hpr.get_x(), hpr.get_y(), hpr.get_z())

    def get_model_hpr(self):
        return self.actor.get_h(), self.actor.get_p(), self.actor.get_r()

    def set_model_hpr(self, h, p, r):
        self.actor.set_hpr(h, p, r)

    def d_set_model_hpr(self, h, p, r):
        self.sendUpdate("set_model_hpr", [h, p, r])
    # endregion

    # region Input
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
    # endregion

    def update(self):
        self.move_input = self.get_relative_input()
        self.handle_rotation()

    @staticmethod
    def play_sound(name):
        messenger.send("play_sound", [name])

    @staticmethod
    def stop_sound(name):
        messenger.send("stop_sound", [name])

    def set_model(self, model_path):
        self.actor.load_model(model_path)
        self.actor.set_scale(player_model_scale)

        # Reposition the model
        box = self.actor.get_tight_bounds()
        size = box[1] - box[0]
        self.actor.set_z(-0.5 * size.get_z())

    def set_score(self, player_id, value):
        self.score = value
        messenger.send("update_score", [player_id, value])

    def d_ready(self):
        self.sendUpdate("set_ready")
