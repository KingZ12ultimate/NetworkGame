from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import UniqueIdAllocator
from Globals import MIN_LEVEL_ZONE, MAX_LEVEL_ZONE


class DLevelManagerAI(DistributedObjectAI):
    MAX_PLAYERS = 2

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.players = []
        self.levels = []

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def request_join(self):
        requester_id = self.air.getAvatarIdFromSender()

        # Add player only if the current number of players is less than the maximum
        if not len(self.players) < self.MAX_PLAYERS:
            self.sendUpdateToAvatarId(requester_id, "join_failure", [])
            return

        player = self.air.createDistributedObject(className="DPlayerAI", zoneId=2)
        self.players.append(player)
        self.sendUpdateToAvatarId(requester_id, "join_success", [player.doId])

        # if we reached maximum players, start the level
        if len(self.players) == self.MAX_PLAYERS:
            self.air.create_level()
            for p in self.players:
                self.air.add_player(p)

    def request_leave(self, player_id):
        player = self.air.doId2do[player_id]
        self.players.remove(player)
        self.air.remove_player(player)
        self.air.sendDeleteMsg(player_id)

    def request_quit(self):
        requester_id = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(requester_id, "left_success", [])
