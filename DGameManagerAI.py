from direct.distributed.DistributedObjectAI import DistributedObjectAI


class DGameManagerAI(DistributedObjectAI):
    def __init__(self, air):
        self.air = air
        DistributedObjectAI.__init__(self, air)

        self.player_list = []

    def delete(self):
        for player in self.player_list:
            self.air.sendDeleteMsg(player.doId)
        self.player_list = []

    def request_join(self):
        """ A client sent a request to join the game. So create a player DO. """
        requester_id = self.air.getAvatarIdFromSender()
        new_player = self.air.createDistributedObject(className="DPlayerAI", zoneId=2)
        self.player_list.append(new_player)
        self.air.add_player(new_player)
        self.sendUpdateToAvatarId(requester_id, "join_success", [new_player.doId])

    def request_leave(self, player_id):
        self.air.world.remove(self.air.doId2do[player_id])
        self.air.sendDeleteMsg(player_id)

        for p in self.player_list:
            if p.doId == player_id:
                self.player_list.remove(p)
                print("Removed player successfully!")
                break
