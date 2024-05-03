from direct.distributed.DistributedObject import DistributedObject
from direct.showbase.MessengerGlobal import messenger


class DLevelManager(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)
        self.level_zone = -1

    def announceGenerate(self):
        DistributedObject.announceGenerate(self)
        self.cr.level_manager = self

    def delete(self):
        print("Level manager deleted")
        DistributedObject.delete(self)

    def d_request_join(self, max_player):
        self.sendUpdate("request_join", [max_player])

    def d_request_leave(self, level_id, player_id):
        self.sendUpdate("request_leave", [level_id, player_id])
        self.cr.sendDeleteMsg(self.cr.player.doId)
        self.cr.sendDeleteMsg(self.cr.level.doId)

        interest_zones = self.cr.interestZones
        interest_zones.remove(self.level_zone)
        self.cr.setInterestZones(interest_zones)
        self.level_zone = -1

    def d_request_quit(self):
        self.sendUpdate("request_quit")

    def join_success(self, join_params):
        # fetch the parameters
        i = 0
        level_zone = join_params[i]
        i += 1
        level_id = join_params[i]
        i += 1
        player_id = join_params[i]

        self.level_zone = level_zone
        self.cr.local_level_id = level_id
        self.cr.local_player_id = player_id

        interest_zones = self.cr.interestZones
        interest_zones.append(level_zone)
        self.cr.setInterestZones(interest_zones)

        self.cr.relatedObjectMgr.requestObjects(
            [level_id, player_id],
            allCallback=self.level_manifested
        )

    def level_manifested(self, all_objects):
        self.cr.level = self.cr.doId2do[self.cr.local_level_id]
        self.cr.player = self.cr.doId2do[self.cr.local_player_id]
        self.cr.player.d_ready()
        print("Level manifested")

    def left_success(self):
        self.delete()
