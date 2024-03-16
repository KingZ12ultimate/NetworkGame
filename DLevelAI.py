from direct.distributed.DistributedNodeAI import DistributedNodeAI
from Globals import BulletRigidBodyNP
from DCherryAI import DCherryAI


class DLevelAI(DistributedNodeAI, BulletRigidBodyNP):

    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)
        BulletRigidBodyNP.__init__(self, "Terrain")

        self.cherries: list[DCherryAI] = []
