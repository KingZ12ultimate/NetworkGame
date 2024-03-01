import random

from direct.distributed.DistributedSmoothNodeAI import DistributedSmoothNodeAI
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import Vec2, Vec3
from Helpers import BulletRigidBodyNP


class DPlayerAI(DistributedSmoothNodeAI, BulletRigidBodyNP):
    """ Player distributed object that resides on the AI server side.
     Responsible for gathering data from player, process it and send results back. """
    def __init__(self, air, pos=Vec3(0, 0, 0), max_speed=15.0,
                 player_input_space=None):
        DistributedSmoothNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Player")

        # Input parameters
        self.move_input = Vec2.zero()
        self.jump_pressed = False

        # Setting physical properties and constrains
        self.max_speed = max_speed
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 150.0
        self.friction = 100.0
        self.air_friction = 3.0
        self.gravity_multiplier = 5.0
        self.set_pos(random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0), 0)

    def update(self, dt):
        """Adjusts the player's velocity according to the received input."""
        self.node().set_active(True)  # prevents unwanted sleeping of the rigid body
        if self.move_input == Vec2.zero():
            friction_amount = self.friction * dt
            if friction_amount > self.velocity.length():
                self.velocity.set(0.0, 0.0, 0.0)
            else:
                friction_vec = -self.velocity.normalized() * friction_amount
                self.velocity += friction_vec
        else:
            self.velocity += self.move_input * self.acceleration * dt

        # Clamp velocity on XY plane
        self.velocity.set_z(0)
        if self.velocity.length() > self.max_speed:
            self.velocity.normalize()
            self.velocity *= self.max_speed

        self.velocity.set_z(self.node().get_linear_velocity().get_z())
        self.node().set_linear_velocity(self.velocity)

    def d_request_capsule_params(self):
        self.sendUpdate("request_capsule_params")

    def d_request_input(self):
        self.sendUpdate("request_input")

    def capsule_params(self, radius, height, up):
        messenger.send("capsule-params-ready", [radius, height, up])

    def receive_input(self, p_input):
        move_input = Vec2(p_input[0], p_input[1])
        jump_pressed = p_input[2]

    def delete(self):
        print("deleting player object AI", self.doId)
        DistributedSmoothNodeAI.delete(self)
