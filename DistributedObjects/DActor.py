from direct.distributed.DistributedNode import DistributedNode
from direct.actor.Actor import Actor


class DActor(DistributedNode):
    def __init__(self, cr):
        DistributedNode.__init__(self, cr)
        self.actor = Actor()
        self.actor.reparent_to(self)
        self.current_animation = None

    def announceGenerate(self):
        DistributedNode.announceGenerate(self)
        self.reparent_to(base.render)

    def delete(self):
        self.actor.cleanup()
        self.remove_node()
        DistributedNode.delete(self)

    def play(self, anim):
        anim_control = self.actor.get_anim_control(anim)
        if not anim_control.is_playing():
            self.actor.play(anim)
            self.current_animation = anim

    def loop(self, anim):
        anim_control = self.actor.get_anim_control(anim)
        if not anim_control.is_playing():
            self.actor.loop(anim)
            self.current_animation = anim

    def stop(self):
        if self.current_animation is None:
            return
        anim_control = self.actor.get_anim_control(self.current_animation)
        if anim_control.is_playing():
            self.actor.stop()
