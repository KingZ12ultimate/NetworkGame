import math
from panda3d.core import Point3, Vec3, Quat, NodePath, BitMask32
from panda3d.bullet import BulletRigidBodyNode


HOST = '127.0.0.1'
PORT = 4400

SERVER_MANAGERS = 1
GAME_MANAGERS = 2
MIN_LEVEL_ZONE = 1000
MAX_LEVEL_ZONE = 2000
MIN_LEVEL_ID = 1000
IDS_PER_LEVEL = 500


masks = {
    "player": BitMask32.bit(0),
    "terrain": BitMask32.bit(1)
}


def lerp(a, b, t): return a * (1 - t) + b * t


def clamp_angle(x):
    while not (0 <= x < 360):
        if x < 0:
            x += 360
        else:
            x -= 360
    return x


def delta_angle(x, y):
    d = y - x
    return (d + 180) % 360 - 180


def _distance(a: Vec3 | Point3, b: Vec3 | Point3): return (b - a).length()


def orthogonal(v: Vec3) -> Vec3:
    other = Vec3(1, 0, 0)
    if v == other:
        other = Vec3(0, 1, 0)
    return Vec3.cross(v, other)


def get_rotation_between(u: Vec3, v: Vec3):
    dot = Vec3.dot(u, v)
    lengths = math.sqrt(u.length_squared() * v.length_squared())

    # Check if the vectors are opposites. If so, the rotation is 180 degrees about any axis orthogonal to vector U.
    if dot / lengths == -1:
        return Quat(0, orthogonal(u).normalized())

    res = Quat(dot + lengths, Vec3.cross(u, v))
    res.normalize()
    return res


def move_towards_angle(current, target, max_delta):
    delta = delta_angle(current, target)
    if delta == 0:
        return current
    elif delta > 0:
        return clamp_angle(current + max_delta)
    else:
        return clamp_angle(current - max_delta)


class BulletRigidBodyNP(NodePath):
    def __init__(self, name: str):
        NodePath.__init__(self, BulletRigidBodyNode(name))
