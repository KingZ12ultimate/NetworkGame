from panda3d.bullet import BulletGhostNode, BulletSphereShape
from panda3d.core import BitMask32


class Ghost:
    def __init__(self):
        self.model = base.loader.load_model("models/frowney")
        self.ghost_np = base.render.attach_new_node(BulletGhostNode("Ghost"))
        self.model.reparent_to(self.ghost_np)

        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = max(size.get_x(), size.get_y(), size.get_z()) * 0.5
        self.ghost_np.node().add_shape(BulletSphereShape(radius))
        self.ghost_np.reparent_to(base.render)
        self.ghost_np.set_collide_mask(BitMask32.bit(1))
        base.world.attach(self.ghost_np.node())

        base.task_mgr.add(self.update, "hi")

    def update(self, task):
        if self.ghost_np.node().get_num_overlapping_nodes() > 0:
            for node in self.ghost_np.node().get_overlapping_nodes():
                print(node)
        return task.cont
