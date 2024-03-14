# imports for the engine
from direct.showbase.ShowBase import ShowBase
from direct.showbase.MessengerGlobal import messenger

from direct.distributed.ClientRepository import ClientRepository
from panda3d.core import URLSpec, ConfigVariableInt, ConfigVariableString
from panda3d.core import Vec2
from DGameManager import DGameManager
from DPlayer import DPlayer
from DLevel import DLevel


class GameClientRepository(ClientRepository):
    def __init__(self, base: ShowBase):
        dc_file_names = ["direct.dc", "ListOfClasses.dc"]
        self.base = base

        # distributed objects for our game
        self.game_mgr: DGameManager | None = None
        self.player: DPlayer | None = None
        self.level: DLevel | None = None

        self.move_input = Vec2.zero()
        self.jump_pressed = False

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

    def lostConnection(self):
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
        self.accept(self.uniqueName("GameManagerGenerated"), self.game_mgr_generated)
        self.accept(self.uniqueName("LevelGenerated"), self.level_generated)
        self.setInterestZones([1, 2])

        print("Client Ready")
        messenger.send("client-ready")

    def update(self):
        self.player.update()
        self.player.d_send_input()
        self.level.terrain.update()

    def game_mgr_generated(self, do_id):
        print("Game manager generated: ", str(do_id))
        self.game_mgr = self.doId2do[do_id]

    def level_generated(self, do_id):
        print("Level generated")
        self.level = self.doId2do[do_id]

    def add_player(self, do_id):
        print("Player object generated: " + str(do_id))
        self.player = self.doId2do[do_id]
        messenger.send("player-ready")

    def request_join(self):
        if not self.game_mgr:
            return

        self.game_mgr.d_request_join()

    def request_leave(self):
        if not self.game_mgr:
            return

        self.game_mgr.d_request_leave(self.player.doId)
