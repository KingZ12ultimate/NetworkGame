import random

from DistributedObjects.DActorAI import DActorAI
from direct.fsm.FSM import FSM
from panda3d.bullet import BulletCapsuleShape, Z_up
from panda3d.core import Vec3
from math import cos, radians
from Globals import BulletRigidBodyNP, masks, player_model_scale


class DPlayerAI(DActorAI, BulletRigidBodyNP, FSM):
    """ Player distributed object that resides on the AI server side.
     Responsible for gathering data from player, process it and send results back. """
    def __init__(self, air, level, model_path, max_speed=20.0):
        DActorAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Player")
        FSM.__init__(self, "Player")

        self.level = level
        self.model_path = model_path
        self.state_update_func = self.idle_update
        self.state = "Idle"
        self.ready = False

        # Input parameters
        self.move_input = Vec3(0, 0, 0)
        self.jump_pressed = False

        # Setting physical properties and constrains
        self.max_speed = max_speed
        self.velocity = Vec3(0, 0, 0)
        self.min_speed = 0.01
        self.acceleration = 150.0
        self.friction = 100.0

        self.max_ground_angle = 45
        self.contact_normal = Vec3(0, 0, 0)
        self.num_ground_contacts = 0
        self.on_ground = lambda: self.num_ground_contacts > 0

        # Setting jump attributes
        self.jump_buffer = 0.5
        self.jump_buffer_timer = 0.0
        self.time_to_apex = 0.3
        self.jump_height = 4
        self.__jump_speed = 2 * self.jump_height / self.time_to_apex
        self.__jump_gravity = -self.__jump_speed / self.time_to_apex

        self.set_pos(random.uniform(-10.0, 10.0), random.uniform(-10.0, 10.0), 10)
        self.set_collide_mask(masks["terrain"] | masks["cherry"])

        self.model = base.loader.load_model(model_path)
        self.model.set_scale(player_model_scale)
        self.skin_width = 0.05

        self.score = 0

    def announceGenerate(self):
        DActorAI.announceGenerate(self)
        self.node().set_name(self.node().get_name() + "-" + str(self.doId))

    def delete(self):
        print("deleting player object AI", self.doId)
        self.cleanup()
        self.remove_node()
        DActorAI.delete(self)

    # region Finite State Machine
    def enterIdle(self):
        self.state_update_func = self.idle_update
        self.d_loop("Idle")

    def enterRun(self):
        self.state_update_func = self.run_update
        self.d_loop("Run")
        self.d_play_sound("run")

    def exitRun(self):
        self.d_stop_sound("run")
        self.defaultExit()

    def enterJump(self):
        self.state_update_func = self.jump_update
        self.node().setGravity(Vec3(0, 0, self.__jump_gravity))
        amount = self.__jump_speed
        if self.velocity.get_z() > 0:
            amount -= self.velocity.get_z()
        self.velocity.add_z(amount)
        self.jump_buffer_timer = -1
        self.d_play("Jump")

    def defaultExit(self):
        self.d_stop()
        FSM.defaultExit(self)

    def idle_update(self):
        if self.on_ground() and self.jump_buffer_timer > 0.0:
            self.request("Jump")
        elif self.velocity.length_squared() > self.min_speed:
            self.request("Run")

    def run_update(self):
        if self.on_ground() and self.jump_buffer_timer > 0.0:
            self.request("Jump")
        elif self.velocity.length_squared() < self.min_speed:
            self.request("Idle")

    def jump_update(self):
        if self.on_ground() and self.velocity.get_z() < 0:
            if self.velocity.length_squared() < self.min_speed:
                self.request("Idle")
            else:
                self.request("Run")
    # endregion

    # region Physics
    def add_collider(self):
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = size.get_y() * 0.5 + self.skin_width
        height = size.get_z() - 2 * radius

        self.node().add_shape(BulletCapsuleShape(radius, height, Z_up))

    def start_jump_buffer_timer(self):
        self.jump_buffer_timer = self.jump_buffer

    def evaluate_collisions(self):
        result = self.level.world.contact_test(self.node(), masks["terrain"])
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

        if self.jump_pressed:
            self.start_jump_buffer_timer()

    def clear_state(self):
        self.num_ground_contacts = 0
        self.contact_normal = Vec3.zero()
        self.jump_pressed = False

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

        if self.state_update_func is not None:
            self.state_update_func()

        self.jump_buffer_timer -= dt
        self.node().set_linear_velocity(self.velocity)
        self.clear_state()
        self.evaluate_collisions()
    # endregion

    def set_ready(self):
        self.ready = True

    def send_input(self, p_input):
        """Receives player input"""
        self.move_input = Vec3(p_input[0], p_input[1], p_input[2])
        self.jump_pressed = p_input[3]

    def d_set_model(self):
        self.sendUpdate("set_model", [self.model_path])

    def d_add_score(self, value):
        self.score += value
        self.sendUpdate("set_score", [self.score])

    def d_play_sound(self, name):
        self.sendUpdate("play_sound", [name])

    def d_stop_sound(self, name):
        self.sendUpdate("stop_sound", [name])
