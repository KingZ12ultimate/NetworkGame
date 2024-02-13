from direct.distributed.DistributedObject import DistributedObject


class DGameObject(DistributedObject):
    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

    def send_game_data(self, data):
        """ Method that can be called from the clients with a sendUpdate call """
        print(data)

    def d_send_game_data(self):
        """ A method to send an update message to the server.  The d_ stands
        for distributed """
        # send the message to the server
        self.sendUpdate("send_game_data", [("ValueA", 123, 1.25)])
