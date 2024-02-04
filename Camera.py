import math
import numpy as np

from BaseContainer import base
from panda3d.core import NodePath, Vec2, Quat
from Helpers import lerp, _distance, move_towards_angle, delta_angle
from Input import global_input


class Camera:
    def __init__(self, camera: NodePath, focus: NodePath, distance, focus_radius,
                 focus_centering=0.5, rotation_speed=90, min_pitch=-30, max_pitch=60,
                 align_delay=5, align_smooth_range=45):
        self.cam = camera

        # Camera position variables
        self.focus = focus
        self.focus_point = focus.get_pos()
        self.previous_focus_point = self.focus_point
        self.distance = distance
        self.focus_radius = max(focus_radius, 0)
        self.focus_centering = np.clip(focus_centering, 0, 1)

        # Camera orientation variables
        self.orbit_angles = Vec2(0, 45)  # x component is heading, y component is pitch
        self.rotation_speed = np.clip(rotation_speed, 1, 360)
        self.min_pitch = np.clip(min_pitch, -89, 89)
        self.max_pitch = np.clip(max_pitch, min_pitch, 89)
        self.align_delay = max(align_delay, 0)
        self.align_smooth_range = np.clip(align_smooth_range, 0, 90)
        self.last_manual_rotation_time = 0

        self.cam.set_z(5)
        initial_rotation = Quat()
        initial_rotation.set_hpr((self.orbit_angles.get_x(), -self.orbit_angles.get_y(), 0))
        self.cam.set_quat(initial_rotation)

    @staticmethod
    def get_angle(direction: Vec2):
        angle = math.degrees(math.acos(direction.get_y()))
        return angle if direction.get_x() < 0 else 360 - angle

    def manual_rotation(self, dt):
        look_input = global_input.look_input
        if look_input != Vec2.zero():
            self.orbit_angles += look_input * self.rotation_speed * dt
            self.last_manual_rotation_time = base.clock.get_real_time()
            return True
        return False

    def automatic_rotation(self, dt):
        if base.clock.get_real_time() - self.last_manual_rotation_time < self.align_delay:
            return False

        movement = self.focus_point.get_xy() - self.previous_focus_point.get_xy()
        movement_delta_sqr = movement.length_squared()
        if movement_delta_sqr < 0.001:
            return False

        heading_angle = self.get_angle(movement / math.sqrt(movement_delta_sqr))
        delta_abs = abs(delta_angle(self.orbit_angles.get_x(), heading_angle))
        rotation_change = self.rotation_speed * min(dt, movement_delta_sqr)
        if delta_abs < self.align_smooth_range:
            rotation_change *= delta_abs / self.align_smooth_range
        elif 180 - delta_abs < self.align_smooth_range:
            rotation_change *= (180 - delta_abs) / self.align_smooth_range
        self.orbit_angles.set_x(move_towards_angle(self.orbit_angles.get_x(), heading_angle, rotation_change))
        return True

    def constrain_angles(self):
        self.orbit_angles.set_y(np.clip(self.orbit_angles.get_y(), self.min_pitch, self.max_pitch))
        if self.orbit_angles.get_x() < 0:
            self.orbit_angles.add_x(360)
        elif self.orbit_angles.get_x() >= 360:
            self.orbit_angles.add_x(-360)

    def update(self, dt):
        self.update_focus_point(dt)
        look_rotation = Quat()
        if self.manual_rotation(dt) or self.automatic_rotation(dt):
            self.constrain_angles()
            look_rotation.set_hpr((self.orbit_angles.get_x(), -self.orbit_angles.get_y(), 0))
        else:
            look_rotation = self.cam.get_quat()
        look_dir = look_rotation.get_forward()
        look_pos = self.focus_point - look_dir * self.distance
        self.cam.set_pos_quat(look_pos, look_rotation)

    def update_focus_point(self, dt):
        self.previous_focus_point = self.focus_point
        target = self.focus.get_pos()
        if self.focus_radius > 0:
            distance = _distance(target, self.focus_point)
            t = 1
            if distance > 0.01 and self.focus_centering > 0:
                t = math.pow(1 - self.focus_centering, dt)
            if distance > self.focus_radius:
                t = min(t, self.focus_radius / distance)
            self.focus_point = lerp(target, self.focus_point, t)
        else:
            self.focus_point = target
