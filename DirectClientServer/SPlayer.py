from direct.distributed.PyDatagram import PyDatagram
from panda3d.core import Connection, QueuedConnectionReader, ConnectionWriter
from panda3d.core import Vec3
from BulletRigidBodyNP import BulletRigidBodyNP


class SPlayer(BulletRigidBodyNP):
    def __init__(self, connection: Connection, c_reader: QueuedConnectionReader, c_writer: ConnectionWriter):
        BulletRigidBodyNP.__init__(self, "Player " + str(self.num_players))
        self.connection = connection
        self.c_reader = c_reader
        self.c_writer = c_writer
