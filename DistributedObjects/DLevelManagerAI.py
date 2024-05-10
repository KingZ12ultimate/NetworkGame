import Globals

from direct.distributed.DistributedObjectAI import DistributedObjectAI
from panda3d.core import UniqueIdAllocator
from DistributedObjects.DLevelAI import DLevelAI
from DistributedObjects.DPlayerAI import DPlayerAI


class DLevelManagerAI(DistributedObjectAI):
    MAX_PLAYERS = 2

    def __init__(self, air):
        DistributedObjectAI.__init__(self, air)

        self.levels = []
        self.air.level_zone_allocator = UniqueIdAllocator(
            Globals.MIN_LEVEL_ZONE,
            Globals.MAX_LEVEL_ZONE
        )

        self.task_chain_name = "level-update-chain"
        base.task_mgr.setupTaskChain(self.task_chain_name, numThreads=4)

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
            found_level = self.request_create_level(max_players)

        model_path = None
        paths = list(found_level.player_models.keys())
        for path in paths:
            if not found_level.player_models[path]:
                model_path = path
                found_level.player_models[path] = True
                break

        player = DPlayerAI(self.air, found_level, model_path)

        self.air.createDistributedObject(
            distObj=player,
            zoneId=found_level.zoneId
        )
        found_level.add_player(player)

        parameters = (
            found_level.zoneId,
            found_level.doId,
            player.doId
        )

        self.sendUpdateToAvatarId(requester_id, "join_success", [parameters])

    def request_leave(self, level_id, player_id):
        matching_levels = filter(
            lambda level: level.doId == level_id,
            self.levels
        )
        found_level = next(matching_levels, None)
        if not found_level:
            print("leave request from a non-existent level")
            return
        found_level.remove_player(player_id)

        # remove the level from the list if there are no players left
        if len(found_level.players) == 0:
            self.levels.remove(found_level)
            self.air.sendDeleteMsg(level_id)

    def request_create_level(self, max_players):
        """ Creates a new level with the specified maximum amount of players and returns it. """
        if max_players < 2 or max_players > 4:
            print("level creation failed, player amount out of range: {} (Min: 2 | Max: 4)".format(max_players))

        new_level = DLevelAI(
            self.air,
            max_players,
        )

        new_level_obj = self.air.createDistributedObject(
            distObj=new_level,
            zoneId=self.air.level_zone_allocator.allocate()
        )

        self.levels.append(new_level)
        return new_level
