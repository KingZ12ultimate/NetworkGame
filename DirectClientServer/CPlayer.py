from direct.distributed.PyDatagram import PyDatagram
from panda3d.core import Connection, QueuedConnectionReader, ConnectionWriter
from panda3d.core import Vec3
from BulletRigidBodyNP import BulletRigidBodyNP
from ConnectionConstants import ConnectionConstants


class CPlayer(BulletRigidBodyNP):
    """Player instance on the client-side."""
    num_players = 0

    def __init__(self, connection: Connection, c_reader: QueuedConnectionReader, c_writer: ConnectionWriter):
        self.num_players += 1
        BulletRigidBodyNP.__init__(self, "Player " + str(self.num_players))
        self.connection = connection
        self.c_reader = c_reader
        self.c_writer = c_writer

        self.model = base.loader.load_model("Models/panda")
        print(self.model)
        self.model.set_scale(0.5)
        self.model.reparent_to(self)

        # Announce generate
        generate_datagram = PyDatagram()
        generate_datagram.add_uint8(ConnectionConstants.CREATE_OBJECT)
        generate_datagram.add_string("Player")
        self.c_writer.send(generate_datagram, self.connection)

    def d_set_pos(self, pos: Vec3):
        self.set_pos(pos)
        pos_datagram = PyDatagram()
        pos_datagram.add_float64(pos.get_x())
        pos_datagram.add_float64(pos.get_y())
        pos_datagram.add_float64(pos.get_z())
        self.c_writer.send(pos_datagram, self.connection)
