from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DGameManagerAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def request_join(self):
        requester_id = self.air.getAvatarIdFromSender()
        player = self.air.createDistributedObject(className="DPlayerAI", zoneId=2)
        self.air.add_player(player)
        self.sendUpdateToAvatarId(requester_id, "join_success", [player.doId])

    def request_leave(self, player_id):
        requester_id = self.air.getAvatarIdFromSender()
        player = self.air.doId2do[player_id]
        self.air.remove_player(player)
        self.air.sendDeleteMsg(player_id)
        self.sendUpdateToAvatarId(requester_id, "left_success", [])
