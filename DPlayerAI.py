import random

from direct.distributed.DistributedNodeAI import DistributedNodeAI
from direct.showbase.MessengerGlobal import messenger
from panda3d.bullet import BulletCapsuleShape, Z_up
from panda3d.core import Vec3
from math import cos, radians
from Globals import BulletRigidBodyNP, masks


class DPlayerAI(DistributedNodeAI, BulletRigidBodyNP):
    """ Player distributed object that resides on the AI server side.
     Responsible for gathering data from player, process it and send results back. """
    def __init__(self, air, pos=Vec3(0, 0, 0), max_speed=15.0,
                 player_input_space=None):
        DistributedNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Player")

        # Input parameters
        self.move_input = Vec3(0, 0, 0)
        self.jump_pressed = False

        # Setting physical properties and constrains
        self.max_speed = max_speed
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 150.0
        self.friction = 100.0
        self.air_friction = 3.0
        self.gravity_multiplier = 5.0

        self.max_ground_angle = 45
        self.contact_normal = Vec3(0, 0, 0)
        self.num_ground_contacts = 0
        self.on_ground = lambda: self.num_ground_contacts > 0

        # Setting jump attributes
        self.jump_buffer = 0.2
        self.jump_buffer_timer = 0.0
        self.time_to_apex = 0.3
        self.jump_height = 4
        self.__jump_speed = 2 * self.jump_height / self.time_to_apex
        self.__jump_gravity = -self.__jump_speed / self.time_to_apex

        self.set_pos(random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0), 10)

        self.model = base.loader.load_model("models/panda")
        self.model.set_scale(0.2)
        self.model.reparent_to(self)
        self.skin_width = 0.05

    def delete(self):
        print("deleting player object AI", self.doId)
        DistributedNodeAI.delete(self)

    def add_collider(self):
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = size.get_y() * 0.5 + self.skin_width
        height = size.get_z() - 2 * radius

        # Reposition the model
        self.model.set_z(-0.5 * height - radius)

        self.node().add_shape(BulletCapsuleShape(radius, height, Z_up))

    def evaluate_collisions(self):
        result = self.air.world.contact_test(self.node(), masks["terrain"])
        if result.get_num_contacts() > 0:
            for contact in result.get_contacts():
                normal = contact.get_manifold_point().get_normal_world_on_b()
                if normal.get_z() > cos(radians(self.max_ground_angle)):
                    self.num_ground_contacts += 1
                    self.contact_normal = self.contact_normal + normal

    def update_state(self):
        self.node().set_active(True)  # prevents unwanted sleeping of the rigid body
        if self.on_ground():
            if self.num_ground_contacts > 1:
                self.contact_normal.normalize()
        else:
            self.contact_normal = Vec3.up()

    def clear_state(self):
        self.num_ground_contacts = 0
        self.contact_normal = Vec3.zero()

    def jump(self):
        if self.jump_buffer_timer > 0:
            self.node().setGravity(Vec3(0, 0, self.__jump_gravity))
            amount = self.__jump_speed
            if self.velocity.get_z() > 0:
                amount -= self.velocity.get_z()
            self.velocity.add_z(amount)
            self.jump_buffer_timer = -1

    def update(self, dt):
        """Adjusts the player's velocity according to the received input."""
        self.update_state()
        if self.move_input == Vec3.zero():
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
        if self.on_ground():
            self.jump()
        self.jump_buffer_timer -= dt

        self.node().set_linear_velocity(self.velocity)
        self.clear_state()
        self.evaluate_collisions()

    def send_input(self, p_input):
        """Receives player input"""
        self.move_input = Vec3(p_input[0], p_input[1], p_input[2])
        self.jump_pressed = p_input[3]
        messenger.send("received-input-" + str(self.doId))
