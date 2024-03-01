from direct.distributed.DistributedSmoothNode import DistributedSmoothNode
from panda3d.bullet import BulletCapsuleShape, Z_up
from Helpers import BulletRigidBodyNP
from Input import global_input


class DPlayer(DistributedSmoothNode, BulletRigidBodyNP):
    def __init__(self, cr):
        DistributedSmoothNode.__init__(self, cr)
        BulletRigidBodyNP.__init__(self, "Player")
        self.model = base.loader.load_model("models/panda")
        self.model.set_scale(0.2)
        self.model.reparent_to(self)
        self.skin_width = 0.05
        # self.setCacheable(True)

    def generate(self):
        DistributedSmoothNode.generate(self)
        self.activateSmoothing(True, False)
        self.startSmooth()
        self.start()

    def announceGenerate(self):
        DistributedSmoothNode.announceGenerate(self)
        self.reparent_to(base.render)

    def start(self):
        self.startPosHprBroadcast()

    def disable(self):
        self.stopSmooth()
        DistributedSmoothNode.disable(self)

    def delete(self):
        print("deleting player object", self.doId)
        self.detach_node()
        self.model = None
        DistributedSmoothNode.delete(self)

    def update(self, dt):
        pass

    def add_collider(self):
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = size.get_y() * 0.5 + self.skin_width
        height = size.get_z() - 2 * radius

        # Reposition the model
        self.model.set_z(-0.5 * height - radius)

        self.node().add_shape(BulletCapsuleShape(radius, height, Z_up))

    def request_capsule_params(self):
        """Sends the capsule collider parameters for the rigid body on the server side."""
        box = self.model.get_tight_bounds()
        size = box[1] - box[0]
        radius = size.get_y() * 0.5  # + self.skin_width
        height = size.get_z() - 2 * radius

        # Reposition the model
        self.model.set_z(-0.5 * height - radius)

        self.sendUpdate("capsule_params", [radius, height, Z_up])

    def request_input(self):
        """Converts player input to tuple and sends it to the AI server."""
        move_input = global_input.move_input
        p_input = (int(move_input.get_x()),
                   int(move_input.get_y()),
                   global_input.jump_pressed)
        self.sendUpdate("receive_input", [p_input])
