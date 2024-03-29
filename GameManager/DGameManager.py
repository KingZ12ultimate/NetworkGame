from direct.distributed.DistributedObject import DistributedObject
from direct.showbase.MessengerGlobal import messenger


class DGameManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

    def announceGenerate(self):
        messenger.send(self.cr.uniqueName("GameManagerGenerated"), [self.doId])
        DistributedObject.announceGenerate(self)

    def delete(self):
        print("deleted")
        DistributedObject.delete(self)

    def d_request_join(self):
        self.sendUpdate("request_join")

    def d_request_leave(self, player_id):
        self.sendUpdate("request_leave", [player_id])

    def d_request_quit(self):
        self.sendUpdate("request_quit")

    def join_success(self, player_id):
        self.cr.add_player(player_id)

    def join_failure(self):
        print("Failed to join, full capacity. Try again later")

    def left_success(self):
        self.delete()
