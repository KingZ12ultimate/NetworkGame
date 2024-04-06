from BaseContainer import base
from panda3d.bullet import BulletGhostNode


class Ghost:
    def __init__(self):
        self.model = base.loader.load_model("models/frowney")
        self.ghost_np = base.render.attach_new_node(BulletGhostNode("Ghost"))
        self.model.reparent_to(self.ghost_np)


