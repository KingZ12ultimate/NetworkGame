from direct.distributed.ServerRepository import ServerRepository
from direct.distributed.ClientRepository import ClientRepository
from direct.showbase.ShowBase import ShowBase
from direct.showbase.DirectObject import DirectObject
from panda3d.core import ConfigVariableInt
import builtins


class GameServerRepository(ServerRepository):
    def __init__(self):
        tcp_port = ConfigVariableInt("server port", 4400).get_value()
        dc_file_names = ["direct.dc"]  # May add my own .dc file.
        ServerRepository.__init__(self, tcp_port, dcFileNames=dc_file_names, threadedNet=True)


class MyAIRepository(ClientRepository):
    def __init__(self):
        dc_file_names = ["direct.dc"]
        ClientRepository.__init__(self, dcFileNames=dc_file_names, dcSuffix="AI", threadedNet=True)

    def deallocate_channel(self, doID):
        print("Client left us: ", doID)


class GameServer(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        builtins.simbase = self
        simbase.air = MyAIRepository()


server = GameServer()
server.run()
