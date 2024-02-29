from direct.distributed.DistributedObject import DistributedObject
from direct.showbase.MessengerGlobal import messenger


class DGameManager(DistributedObject):
    def __init__(self, cr):
        self.cr = cr
        DistributedObject.__init__(self, cr)

    def announceGenerate(self):
        messenger.send(self.cr.uniqueName("GameManagerGenerated"), [self.doId])
        DistributedObject.announceGenerate(self)

    def d_request_join(self):
        self.sendUpdate("request_join")

    def d_request_leave(self):
        self.sendUpdate("request_leave", [self.cr.local_player_id])
        self.cr.sendDeleteMsg(self.cr.local_player_id)

        # player = self.cr.doId2do[self.cr.local_player_id]
        # player.delete()

    def join_success(self, player_id):
        print("Joined successfully!")
        messenger.send(self.cr.uniqueName("PlayerObjectGenerated"), [player_id])
        messenger.send("join-success")
