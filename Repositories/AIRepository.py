from direct.distributed.ClientRepository import ClientRepository
from direct.showbase.ShowBase import ShowBase
from direct.task.Task import Task
from panda3d.core import URLSpec, ConfigVariableInt, ConfigVariableString
from panda3d.core import Vec3
from panda3d.bullet import BulletWorld, BulletHeightfieldShape, Z_up
from DistributedObjects.DLevelManagerAI import DLevelManagerAI
from DistributedObjects.DPlayerAI import DPlayerAI
from DistributedObjects.DLevelAI import DLevelAI
from Globals import SERVER_MANAGERS, GAME_MANAGERS, PORT


GRAVITY = Vec3(0, 0, -9.81)


class AIRepository(ClientRepository):
    def __init__(self, base: ShowBase):
        """The AI Repository usually lives on a server and is responsible for
        server side logic that will handle game objects"""

        self.base = base
        self.update_task = None
        self.players = []
        self.game_mgr: DLevelManagerAI | None = None
        self.level: DLevelAI | None = None

        # Create the physics world
        self.world = BulletWorld()
        self.world.set_gravity(GRAVITY)
        self.world_np = self.base.render.attach_new_node("Physics-World")

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
        self.game_mgr = self.createDistributedObject(className='DLevelManagerAI', zoneId=GAME_MANAGERS)

        print("AI Repository Ready")

    def create_level(self):
        self.level = self.createDistributedObject(className='DLevelAI', zoneId=2)

        # Add terrain rigid body to the world
        collider = BulletHeightfieldShape(self.level.height_map, self.level.height, Z_up)
        self.level.node().add_shape(collider)
        self.world.attach(self.level.node())
        self.level.reparent_to(self.world_np)

        self.level.generate_cherries()

    def update(self, task):
        """The main task that will handle game logic, in that order:
            1. gathering player input
            2. processing the input
            3. advance the physics simulation"""
        if not self.players:
            return Task.cont

        dt = self.base.clock.get_dt()

        for player in self.players:
            # self.accept("received-input-" + str(player.doId), player.update, [dt])
            player.update(dt)

        self.level.update()

        self.world.do_physics(dt)

        for player in self.players:
            pos = player.get_pos()
            player.d_setPos(pos.get_x(), pos.get_y(), pos.get_z())

        return Task.cont

    def add_player(self, player: DPlayerAI):
        # Adding a collider
        player.add_collider()

        # Setting physical attributes
        player.node().set_mass(1.0)
        player.node().set_angular_factor(Vec3(0, 0, 1.0))

        # Setting up CCD
        player.node().set_ccd_motion_threshold(1e-07)
        player.node().set_ccd_swept_sphere_radius(0.5)

        # Attaching the player to the world
        self.world.attach(player.node())
        # player.reparent_to(self.world_np)

        self.players.append(player)

        print("Player {} added successfully!".format(player.doId))

    def remove_player(self, player: DPlayerAI):
        # Remove the player from the player list if it appears there.
        for p in self.players:
            if p == player:
                self.players.remove(p)

        self.world.remove(player.node())

    def deallocateChannel(self, do_id):
        """This method will be called whenever a client disconnects from the
        server.  The given doID is the ID of the client who left us."""
        requester_id = self.getAvatarIdFromSender()
        print("Requester left us:", requester_id)
        print("Client left us:", do_id)
