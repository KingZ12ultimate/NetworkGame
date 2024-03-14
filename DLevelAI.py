from direct.distributed.DistributedNodeAI import DistributedNodeAI
from Helpers import BulletRigidBodyNP


class DLevelAI(DistributedNodeAI, BulletRigidBodyNP):

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Terrain")
