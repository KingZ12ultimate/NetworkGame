# imports for the engine
from direct.showbase.ShowBase import ShowBase

from direct.distributed.ClientRepository import ClientRepository
from panda3d.core import URLSpec, ConfigVariableInt, ConfigVariableString
from DGameObject import DGameObject
from AIDGameObject import AIDGameObject

# initialize the engine
base = ShowBase()


class GameClientRepository(ClientRepository):
    def __init__(self):
        dc_file_names = ["direct.dc", "sample.dc"]

        # a distributed object for our game
        self.distributed_object: DGameObject | None = None
        self.ai_d_game_object: AIDGameObject | None = None

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
        self.url = URLSpec("http://{}:{}".format(host_name, tcp_port))

        # Attempt a connection to the server
        self.connect([self.url],
                     successCallback=self.connect_success,
                     failureCallback=self.connect_failure)

    def lost_connection(self):
        """ This should be overridden by a derived class to handle an
                unexpectedly lost connection to the gameserver. """
        # Handle the disconnection from the server.  This can be a reconnect,
        # simply exiting the application or anything else.
        print("Lost connection. Attempts reconnect...")
        self.connect([self.url],
                     successCallback=self.connect_success,
                     failureCallback=self.connect_failure)

    def connect_failure(self, status_code, status_string):
        """ Something went wrong """
        # we could create a reconnect task to try and connect again.
        print("Failed to connect"
              "\nstatus code: {}, status string: {}".format(status_code, status_string))
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
        self.join()

        print("Client Ready")
        base.messenger.send("client-ready")

    def join(self):
        """ Join a game/room/whatever """
        self.accept(self.uniqueName('AIDGameObjectGenerated'), self.ai_d_game_object_generated)

        # set our interest zones to let the client see all distributed objects
        # in those zones
        self.setInterestZones([1, 2])

        # Manifest an object on the server.  The object will have our "base" doId.
        self.distributed_object = DGameObject(self)
        self.createDistributedObject(distObj=self.distributed_object, zoneId=2)

        base.messenger.send("client-joined")
        print("Joined")

    def ai_d_game_object_generated(self, do_id):
        print("AIDGameObject was generated")
        self.ai_d_game_object = self.doId2do[do_id]

    def send_game_data(self):
        if not self.distributed_object:
            return

        print("Send game data")

        # send a message to the server
        self.distributed_object.d_send_game_data()

    def send_roundtrip_to_ai(self):
        if not self.ai_d_game_object:
            return

        print("Initiate roundtrip message to AI Server")
        self.ai_d_game_object.d_request_data_from_ai()
