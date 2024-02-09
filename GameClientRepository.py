from direct.distributed.ClientRepository import ClientRepository
from direct.showbase.ShowBase import ShowBase
from panda3d.core import URLSpec, ConfigVariableInt, ConfigVariableString
import builtins


class GameClientRepository(ClientRepository):
    def __init__(self):
        dc_file_names = ["direct.dc"]

        # a distributed object for our game
        self.distributed_object = None
        self.ai_Dgame_object = None

        ClientRepository.__init__(self, dcFileNames=dc_file_names, threadedNet=True)

        # Set the same port as configured on the server to be able to connect
        # to it
        tcp_port = ConfigVariableInt("server port", 4400).get_value()

        # Set the IP or hostname of the server we want to connect to
        host_name = ConfigVariableString("server host", "127.0.0.1").get_value()

        # Build the URL from the server hostname and port. If your server
        # uses another protocol than http you should change it accordingly.
        # Make sure to pass the connectMethod to the ClientRepository.__init__
        # call too.  Available connection methods are:
        # self.CM_HTTP, self.CM_NET and self.CM_NATIVE
        self.url = URLSpec("https://{}:{}".format(host_name, tcp_port))

        # Attempt a connection to the server
        self.connect([self.url],
                     successCallback=self.connect_success,
                     failureCallback=self.connect_failure)

    def lost_connection(self):
        """ This should be overridden by a derived class to handle an
                unexpectedly lost connection to the gameserver. """
        # Handle the disconnection from the server.  This can be a reconnect,
        # simply exiting the application or anything else.
        exit()

    def connect_failure(self, status_code, status_string):
        """ Something went wrong """
        exit()

    def connect_success(self):
        """ Successfully connected.  But we still can't really do
                anything until we've got the doID range. """

        # Make sure we have interest in the AIRepository defined
        # TimeManager zone, so we always see it even if we switch to
        # another zone.
        self.setInterestZones([1])

        # We must wait for the TimeManager to be fully created and
        # synced before we can enter another zone and wait for the
        # game object.  The uniqueName is important that we get the
        # correct, our sync message from the TimeManager and not
        # accidentally a message from another client.
        self.accept_once(self.uniqueName("gotTimeSync"), self.sync_ready)

    def sync_ready(self):
        """ Now we've got the TimeManager manifested, and we're in
                sync with the server time.  Now we can enter the world.  Check
                to see if we've received our doIdBase yet. """

        # This method checks whether we actually have a valid doID range
        # to create distributed objects yet.
        if self.haveCreateAuthority():
            # we already have one
            self.got_create_ready()
        else:
            # Not yet, keep waiting a bit longer.
            self.accept(self.uniqueName('createReady'), self.got_create_ready)

    def got_create_ready(self):
        """ Ready to enter the world.  Expand our interest to include
                any other zones """

        # This method checks whether we actually have a valid doID range
        # to create distributed objects yet.
        if not self.haveCreateAuthority():
            # Not ready yet.
            return

        # we are ready now, so ignore further createReady events
        self.ignore(self.uniqueName("createReady"))

        # Now the client is ready to create DOs and send and receive data
        # to and from the server


class GameClient(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.cr = GameClientRepository()


client = GameClient()
client.run()
