import builtins

# imports for the engine
from direct.showbase.ShowBase import ShowBase

from Repositories.ServerRepository import GameServerRepository
from Repositories.AIRepository import AIRepository


class GameServer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self, windowType="none")
        builtins.simbase = self
        self.sr = GameServerRepository()

        # The AI Repository to manage server side (AI) clients
        self.air = AIRepository(self)
        simbase.air = self.air
        self.task_mgr.add(self.air.update, "update-task")  # TODO: move this line somewhere else


# start the server
server = GameServer()
server.run()
