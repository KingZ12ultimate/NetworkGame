from BaseContainer import base
from Helpers import get_rotation_between


from direct.interval.LerpInterval import LerpQuatInterval
from math import cos, radians


from panda3d.core import Vec2, Vec3
from panda3d.core import BitMask32
from panda3d.bullet import BulletRigidBodyNode, BulletCapsuleShape, Z_up

from Input import global_input


class Player:
    def __init__(self, model_path: str, pos=Vec3(0, 0, 0), max_speed=15.0,
                 player_input_space=base.render):
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

        self.max_ground_angle = 45
        self.contact_normal = Vec3(0, 0, 0)
        self.num_ground_contacts = 0
        self.on_ground = lambda: self.num_ground_contacts > 0
        self.player_input_space = player_input_space

        # Rotation factors
        self.rotation_factor_per_frame = 0.5
        self.rotation_duration = 0.1
        self.rotation_forward_dir = Vec3(0, -1, 0)
        self.rotation_interval: LerpQuatInterval | None = None

        self.rigid_body_np = base.render.attach_new_node(BulletRigidBodyNode("Player"))
        self.rigid_body_np.node().set_mass(1.0)
        self.rigid_body_np.node().set_angular_factor(Vec3(0, 0, 1.0))
        self.rigid_body_np.set_pos(pos)

        # Setting jump attributes
        self.jump_buffer = 0.2
        self.jump_buffer_timer = 0.0
        self.time_to_apex = 0.3
        self.jump_height = 4
        self.__jump_speed = 2 * self.jump_height / self.time_to_apex
        self.__jump_gravity = -self.__jump_speed / self.time_to_apex

        # Setting colliders and model
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = size.get_y() * 0.5 + self.skin_width
        height = size.get_z() - 2 * radius
        capsule = BulletCapsuleShape(radius, height, Z_up)
        self.rigid_body_np.node().add_shape(capsule)
        self.model.reparent_to(self.rigid_body_np)
        self.model.set_z(-0.5 * height - radius)

        self.mask = BitMask32.bit(0) | BitMask32.bit(1)
        self.rigid_body_np.set_collide_mask(self.mask)
        # self.rigid_body.set_deactivation_enabled(False)

        # Setting up CCD
        self.rigid_body_np.node().set_ccd_motion_threshold(1e-07)
        self.rigid_body_np.node().set_ccd_swept_sphere_radius(0.5)

        base.world.attach_rigid_body(self.rigid_body_np.node())

        global_input.subscribe_to_event("space", self.start_jump_buffer_timer)
        global_input.subscribe_to_event("r", self.reset)

    def get_relative_input(self):
        if self.player_input_space:
            forward = self.player_input_space.get_quat().get_forward()
            forward.set_z(0)
            forward.normalize()
            right = self.player_input_space.get_quat().get_right()
            right.set_z(0)
            right.normalize()
            move_input = global_input.move_input
            return right * move_input.get_x() + forward * move_input.get_y()
        else:
            return Vec3(global_input.move_input, 0)

    def handle_rotation(self):
        if self.rotation_interval is not None:
            if self.rotation_interval.is_playing():
                return

        if global_input.move_input != 0:
            position_to_look = self.get_relative_input()
            target_rotation = get_rotation_between(self.rotation_forward_dir, position_to_look)
            self.rotation_interval = LerpQuatInterval(nodePath=self.model,
                                                      duration=self.rotation_duration,
                                                      quat=target_rotation,
                                                      blendType="easeInOut",
                                                      name="rotationInterval")
            self.rotation_interval.start()

    def evaluate_collisions(self):
        result = base.world.contact_test(self.rigid_body_np.node())
        if result.get_num_contacts() > 0:
            for contact in result.get_contacts():
                normal = contact.get_manifold_point().get_normal_world_on_b()
                if normal.get_z() > cos(radians(self.max_ground_angle)):
                    self.num_ground_contacts += 1
                    self.contact_normal = self.contact_normal + normal

    def update_state(self):
        self.rigid_body_np.node().set_active(True)
        if self.on_ground():
            if self.num_ground_contacts > 1:
                self.contact_normal.normalize()
        else:
            self.contact_normal = Vec3.up()
        self.handle_rotation()

    def clear_state(self):
        self.num_ground_contacts = 0
        self.contact_normal = Vec3.zero()

    def reset(self):
        self.rigid_body_np.node().set_linear_velocity(Vec3.zero())
        self.rigid_body_np.set_pos(0, 0, 5)

    def start_jump_buffer_timer(self):
        self.jump_buffer_timer = self.jump_buffer

    def jump(self):
        if self.jump_buffer_timer > 0:
            base.world.set_gravity(Vec3(0, 0, self.__jump_gravity))
            amount = self.__jump_speed
            if self.velocity.get_z() > 0:
                amount -= self.velocity.get_z()
            self.velocity.add_z(amount)
            self.jump_buffer_timer = -1

    def update(self, dt):
        self.update_state()

        if global_input.move_input == Vec2.zero():
            friction_amount = self.friction * dt
            if friction_amount > self.velocity.length():
                self.velocity.set(0.0, 0.0, 0.0)
            else:
                friction_vec = -self.velocity.normalized() * friction_amount
                self.velocity += friction_vec
        else:
            self.velocity += self.get_relative_input() * self.acceleration * dt

        # Clamp velocity on XY plane
        self.velocity.set_z(0)
        if self.velocity.length() > self.max_speed:
            self.velocity.normalize()
            self.velocity *= self.max_speed

        self.velocity.set_z(self.rigid_body_np.node().get_linear_velocity().get_z())
        if self.on_ground():
            self.jump()
        self.jump_buffer_timer -= dt

        self.rigid_body_np.node().set_linear_velocity(self.velocity)
        self.clear_state()
        self.evaluate_collisions()

