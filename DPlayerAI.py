from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import Vec3
from Helpers import BulletRigidBodyNP


class DPlayerAI(DistributedSmoothNodeAI, BulletRigidBodyNP):
    """ Player distributed object that resides on the AI server side.
     Responsible for gathering data from player, process it and send results back. """
    def __init__(self, air, pos=Vec3(0, 0, 0), max_speed=15.0,
                 player_input_space=base.render):
        DistributedSmoothNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Player")

        # Setting physical properties and constrains
        self.max_speed = max_speed
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 150.0
        self.friction = 100.0
        self.air_friction = 3.0
        self.gravity_multiplier = 5.0

    def update(self, dt):
        pass

    def d_request_capsule_params(self):
        self.sendUpdate("request_capsule_params")

    def capsule_params(self, radius, height, up):
        messenger.send("capsule-params-ready", [radius, height, up])

    def receive_input(self, p_input):
        pass

    def delete(self):
        print("deleting player object AI", self.doId)
        DistributedSmoothNodeAI.delete(self)
