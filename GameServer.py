import builtins

# imports for the engine
from direct.showbase.ShowBase import ShowBase

from ServerRepository import GameServerRepository
from AIRepository import AIRepository


class GameServer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self, windowType="none")
        builtins.simbase = self
        self.sr = GameServerRepository()

        # The AI Repository to manage server side (AI) clients
        self.air = AIRepository()
        simbase.air = self.air


# start the server
server = GameServer()
server.run()
