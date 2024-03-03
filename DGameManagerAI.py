from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DGameManagerAI(DistributedObjectAI):
    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

    def request_join(self):
        player = self.air.createDistributedObject(className="PlayerAI", zoneId=2)
        self.air.add_player(player)

    def request_leave(self, player_id):
        player = self.air.doId2do[player_id]
        self.air.remove_player(player)
        player.sendDeleteMsg()
