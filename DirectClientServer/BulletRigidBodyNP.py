from panda3d.core import NodePath
from panda3d.bullet import BulletRigidBodyNode


class BulletRigidBodyNP(NodePath):
    """Helper class to wrap the behavior of BulletRigidBodyNode with NodePath."""
    def __init__(self, name="Player"):
        NodePath.__init__(self, BulletRigidBodyNode(name))
