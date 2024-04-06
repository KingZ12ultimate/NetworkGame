from direct.distributed.DistributedNode import DistributedNode


class DCherry(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self.model = base.loader.load_model("models/frowney")

        self.model.reparent_to(self)
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        self.model.set_z(-0.5 * size.get_z())

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.reparent_to(base.render)
        self.sendUpdate("request_pos")

    def delete(self):
        self.detach_node()
        DistributedNode.delete(self)
