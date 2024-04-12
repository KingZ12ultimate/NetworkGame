import Globals

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import UniqueIdAllocator
from DLevelAI import DLevelAI


class DLevelManagerAI(DistributedObjectAI):
    MAX_PLAYERS = 2

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)
        self.players = []

        self.levels = []
        self.level_zone_allocator = UniqueIdAllocator(
            Globals.MIN_LEVEL_ZONE,
            Globals.MAX_LEVEL_ZONE
        )

    def announceGenerate(self):
        DistributedObjectAI.announceGenerate(self)

    def delete(self):
        self.levels = []
        DistributedObjectAI.delete(self)

    def request_join(self, max_players):
        requester_id = self.air.getAvatarIdFromSender()

        available_matching_levels = filter(
            lambda level: level.max_players == max_players and level.can_join(),
            self.levels
        )
        found_level = next(available_matching_levels, None)
        if found_level is None:
            print("No level found, creating new one")
            self.request_create_level()
            return

        player = self.air.createDistributedObject(
            className="DPlayerAI",
            zoneId=found_level.zoneId
        )
        found_level.add_player(player)

        parameters = (
            found_level.zoneId,
            found_level.doId,
            player.doId
        )

        self.players.append(player)
        self.sendUpdateToAvatarId(requester_id, "join_success", [parameters])

    def request_leave(self, level_id, player_id):
        matching_levels = filter(
            lambda level: level.doId == level_id,
            self.levels
        )
        found_level = next(matching_levels, None)
        found_level.remove_player(player_id)

        # remove the level from the list if there are no players left
        if len(found_level.players) == 0:
            self.levels.remove(found_level)
            self.air.sendDeleteMsg(level_id)

    def request_create_level(self, max_players):
        if max_players < 2 or max_players > 4:
            print("level creation failed, player amount out of range: {} (Min: 2 | Max: 4)".format(max_players))

        new_level = DLevelAI(
            self.air,
            max_players,
            self.level_zone_allocator.allocate()
        )

        new_level_obj = self.air.createDistributedObject(
            distObj=new_level,
            zoneId=Globals.LEVEL_MANAGER_ZONE
        )

        self.levels.append(new_level)

    def request_quit(self):
        requester_id = self.air.getAvatarIdFromSender()
        self.sendUpdateToAvatarId(requester_id, "left_success", [])
