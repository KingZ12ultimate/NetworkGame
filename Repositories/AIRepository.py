from direct.distributed.ClientRepository import ClientRepository
from panda3d.core import URLSpec, ConfigVariableInt, ConfigVariableString
from Globals import SERVER_MANAGERS, LEVEL_MANAGER_ZONE, PORT


class AIRepository(ClientRepository):
    def __init__(self):
        """The AI Repository usually lives on a server and is responsible for
        server side logic that will handle game objects"""

        self.level_manager = None
        self.level_zone_allocator = None

        # Getting ready to establish a connection
        dc_file_names = ["Assets/direct.dc", "Assets/ListOfClasses.dc"]
        ClientRepository.__init__(self, dcFileNames=dc_file_names, dcSuffix="AI", threadedNet=True)

        tcp_port = ConfigVariableInt("server-port", PORT).get_value()
        host_name = ConfigVariableString("server-host", "127.0.0.1").get_value()

        url = URLSpec("http://{}:{}".format(host_name, tcp_port))

        # Attempt a connection to the server
        self.connect([url],
                     successCallback=self.connect_success,
                     failureCallback=self.connect_failure)

    def lostConnection(self):
        """ This should be overridden by a derived class to handle an
                unexpectedly lost connection to the game server. """
        # Handle the disconnection from the server.  This can be a reconnect,
        # simply exiting the application or anything else.
        exit()

    def connect_failure(self, status_code, status_string):
        """ Something went wrong """
        print("Couldn't connect. Make sure to run server.py first!"
              "\nstatus code: {}, status string: {}".format(status_code, status_string))
        exit()

    def connect_success(self):
        """ Successfully connected.  But we still can't really do
                anything until we've got the doID range. """

        # The Client Repository will throw this event as soon as it has a doID
        # range and would be able to create distributed objects
        self.accept("createReady", self.got_create_ready)

    def got_create_ready(self):
        """Now we're ready to go!"""

        # This method checks whether we actually have a valid doID range
        # to create distributed objects yet.
        if not self.haveCreateAuthority():
            # Not ready yet.
            return

        # we are ready now, so ignore further createReady events
        self.ignore("createReady")

        # Create a Distributed Object by name.  This will look up the object in
        # the dc files passed to the repository earlier
        self.timeManager = self.createDistributedObject(className='TimeManagerAI', zoneId=SERVER_MANAGERS)
        self.level_manager = self.createDistributedObject(className='DLevelManagerAI', zoneId=LEVEL_MANAGER_ZONE)

        print("AI Repository Ready")

    def deallocateChannel(self, do_id):
        """This method will be called whenever a client disconnects from the
        server.  The given doID is the ID of the client who left us."""
        requester_id = self.getAvatarIdFromSender()
        print("Requester left us:", requester_id)
        print("Client left us:", do_id)
