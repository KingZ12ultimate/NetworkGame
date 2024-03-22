# imports for the server
from direct.distributed.ServerRepository import ServerRepository
from panda3d.core import ConfigVariableInt


# the main server class
class GameServerRepository(ServerRepository):
    """The server repository class"""
    def __init__(self):
        """Initialize the server class"""

        tcp_port = ConfigVariableInt("server-port", 4400).get_value()

        # list of all required .dc files
        dc_file_names = ["Assets/direct.dc", "Assets/ListOfClasses.dc"]  # May add my own .dc file.

        # initialize a threaded server on this machine with
        # the port number and the .dc filenames
        ServerRepository.__init__(self, tcp_port, dcFileNames=dc_file_names, threadedNet=True)
