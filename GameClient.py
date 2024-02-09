from panda3d.core import QueuedConnectionManager
from panda3d.core import QueuedConnectionReader
from panda3d.core import ConnectionWriter
from direct.distributed.PyDatagram import PyDatagram
from direct.task.Task import Task
from direct.showbase.ShowBase import ShowBase


port_address = 9099
ip_address = "127.0.0.1"
timeout = 3000


class Client(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.c_manager = QueuedConnectionManager()
        self.c_reader = QueuedConnectionReader(self.c_manager, 0)
        self.c_writer = ConnectionWriter(self.c_manager, 0)

        self.my_connection = self.c_manager.open_TCP_client_connection(ip_address, port_address, timeout)
        if self.my_connection:
            self.c_reader.add_connection(self.my_connection)

        self.task_mgr.add(self.update, "update")

    def update(self, task):
        message = input()
        if message == "quit":
            self.c_manager.close_connection(self.my_connection)
        my_py_datagram = PyDatagram()
        my_py_datagram.add_string(message)
        self.c_writer.send(my_py_datagram, self.my_connection)
        return Task.cont


client = Client()
client.run()
