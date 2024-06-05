from direct.distributed.DistributedNode import DistributedNode


class DCherry(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        model = base.loader.load_model("Assets/Models/cherries.glb")

        model.reparent_to(self)
        box = model.get_tight_bounds()
        size = box[1] - box[0]
        model.set_z(-0.5 * size.get_z())

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.reparent_to(base.render)
        self.sendUpdate("request_pos")

    def delete(self):
        self.remove_node()
        DistributedNode.delete(self)
