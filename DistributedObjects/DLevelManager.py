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
        print("deleted")
        DistributedObject.delete(self)

    def d_request_join(self):
        self.sendUpdate("request_join")

    def d_request_leave(self, player_id):
        self.sendUpdate("request_leave", [player_id])

    def d_request_create_level(self):
        pass

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

        interest_zones = self.cr.interestZones
        interest_zones.append(level_zone)
        self.cr.setInterestZones(interest_zones)

        self.cr.add_player(player_id)

    def join_failure(self):
        print("Failed to join, full capacity. Try again later")

    def left_success(self):
        self.delete()
