from panda3d.core import QueuedConnectionManager, QueuedConnectionListener, QueuedConnectionReader
from panda3d.core import ConnectionWriter, PointerToConnection, NetAddress, NetDatagram
from direct.distributed.PyDatagramIterator import PyDatagramIterator
from direct.task.Task import Task
from direct.showbase.ShowBase import ShowBase
from ConnectionConstants import ConnectionConstants
from SPlayer import SPlayer


port_address = 9099


class Server(ShowBase):
    def __init__(self):
        ShowBase.__init__(self, windowType="none")

        self.c_manager = QueuedConnectionManager()
        self.c_listener = QueuedConnectionListener(self.c_manager, 0)
        self.c_reader = QueuedConnectionReader(self.c_manager, 0)
        self.c_writer = ConnectionWriter(self.c_manager, 0)

        self.active_connections = []  # We'll want to keep track of these later
        self.player_list = []

        back_log = 1000
        tcp_socket = self.c_manager.open_TCP_server_rendezvous(port_address, back_log)
        self.c_listener.add_connection(tcp_socket)

        self.task_mgr.add(self.tsk_listener_polling, "Poll the connection listener", -39)
        self.task_mgr.add(self.tsk_reader_polling, "Poll the connection reader", -40)

    def tsk_listener_polling(self, task_data):
        if self.c_listener.new_connection_available():
            rendezvous = PointerToConnection()
            net_address = NetAddress()
            new_connection = PointerToConnection()

            if self.c_listener.get_new_connection(rendezvous, net_address, new_connection):
                new_connection = new_connection.p()
                self.active_connections.append(new_connection)
                self.c_reader.add_connection(new_connection)
        return Task.cont

    def tsk_reader_polling(self, task_data):
        if self.c_reader.data_available():
            datagram = NetDatagram()
            if self.c_reader.get_data(datagram):
                iterator = PyDatagramIterator(datagram)
                msg_id = iterator.get_uint8()
                if msg_id == ConnectionConstants.CREATE_OBJECT:
                    class_name = "S" + iterator.get_string()
                    self.player_list.append(self.create_object(class_name, datagram.get_connection()))
                    print("Added player")
        return Task.cont

    def create_object(self, class_name, connection):
        dclass = globals()[class_name]
        return dclass(connection, self.c_reader, self.c_writer)


server = Server()
server.run()
