from direct.distributed.DistributedNode import DistributedNode


class DCherry(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
