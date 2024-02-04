from __future__ import annotations
import direct.showbase.ShowBaseGlobal

from typing import TYPE_CHECKING

from panda3d.core import Vec2, Vec3, Vec4, Point3
from panda3d.bullet import BulletRigidBodyNode, BulletCapsuleShape, Z_up

from Input import global_input
if TYPE_CHECKING:
    from Game import Game
base: Game = direct.showbase.ShowBaseGlobal.base


class Player:
    def __init__(self, model_path: str, pos=Vec3(0, 0, 0), max_speed=10.0):
        self.model = base.loader.load_model(model_path)
        self.model.set_scale(0.2)

        # Setting physical properties and constrains
        self.max_speed = max_speed
        self.velocity = Vec3(0, 0, 0)
        self.acceleration = 150.0
        self.friction = 100.0
        self.air_friction = 3.0
        self.gravity_multiplier = 5.0
        self.skin_width = 0.05

        # Setting jump attributes
        self.jump_buffer = 0.2
        self.jump_buffer_timer = 0.0
        self.time_to_apex = 0.3
        self.jump_height = 4
        self.__jump_velocity = 2 * self.jump_height / self.time_to_apex
        self.__jump_gravity = self.__jump_velocity / self.time_to_apex

        # Setting colliders and model
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = size.get_y() * 0.5 + self.skin_width
        height = size.get_z() - 2 * radius
        capsule = BulletCapsuleShape(radius, height, Z_up)
        self.rigid_body = BulletRigidBodyNode("Player")
        self.rigid_body.set_mass(1.0)
        self.rigid_body.set_kinematic(True)
        self.rigid_body.add_shape(capsule)
        self.rigid_body_path = base.render.attach_new_node(self.rigid_body)
        self.rigid_body_path.set_pos(pos)

        self.model.reparent_to(self.rigid_body_path)
        self.model.set_z(-0.5 * height - radius)
        base.world.attach_rigid_body(self.rigid_body_path.node())

        global_input.subscribe_to_event("space", self.start_jump_buffer_timer)

    def start_jump_buffer_timer(self):
        self.jump_buffer_timer = self.jump_buffer

    def jump(self):
        # base.gravity_handler.gravity = self.__jump_gravity
        # base.gravity_handler.add_velocity(self.__jump_velocity)
        self.jump_buffer_timer = -1

    def update(self, dt):
        speed = self.velocity.length()
        if speed > self.max_speed:
            self.velocity.normalize()
            self.velocity *= self.max_speed
            speed = self.max_speed

        # if self.jump_buffer_timer >= 0:
        #     self.jump()
        # self.jump_buffer_timer -= dt

        if global_input.move_input == Vec2.zero():
            friction_amount = self.friction * dt
            if friction_amount > speed:
                self.velocity.set(0.0, 0.0, 0.0)
            else:
                friction_vec = -self.velocity.normalized() * friction_amount
                self.velocity += friction_vec

        self.velocity += Vec3(global_input.move_input, 0.0) * self.acceleration * dt
        self.rigid_body.set_linear_velocity(self.rigid_body.get_linear_velocity() + self.velocity)

