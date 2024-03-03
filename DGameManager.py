from direct.distributed.DistributedObject import DistributedObject
from direct.showbase.MessengerGlobal import messenger


class DGameManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

    def announceGenerate(self):
        messenger.send(self.cr.uniqueName("GameManagerGenerated"), [self.doId])
        DistributedObject.announceGenerate(self)

    def d_request_join(self):
        self.sendUpdate("request_join")

    def d_request_leave(self, player_id):
        self.sendUpdate("request_leave", [player_id])
