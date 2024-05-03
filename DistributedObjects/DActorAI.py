from direct.distributed.DistributedNodeAI import DistributedNodeAI


class DActorAI(DistributedNodeAI):
    def __init__(self, air):
        DistributedNodeAI.__init__(self, air)

    def d_play(self, anim):
        self.sendUpdate("play", [anim])

    def d_loop(self, anim):
        self.sendUpdate("loop", [anim])

    def d_stop(self):
        self.sendUpdate("stop")
