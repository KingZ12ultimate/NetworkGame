from direct.showbase.MessengerGlobal import messenger
from direct.distributed.DistributedObject import DistributedObject


class AIDGameObject(DistributedObject):
    """ This class is a DistributedObject which will be created and managed by the
    AI Repository. """

    def __init__(self, cr):
        DistributedObject.__init__(self, cr)

    def announceGenerate(self):
        """ The AI has created this object, so we send its distributed object ID
        over to the client.  That way the client can actually grab the object
        and use it to communicate with the AI.  Alternatively store it in the
        Client Repository in self.cr """
        messenger.send(self.cr.uniqueName("AIDGameObjectGenerated"), [self.doId])
        DistributedObject.announceGenerate(self)

    def d_request_data_from_ai(self):
        """ Request some data from the AI and passing it some data from us. """
        data = ("Some Data", 1, -1.25)
        print("Sending game data: ", data)
        self.sendUpdate("message_roundtrip_to_ai", [data])

    def message_roundtrip_to_client(self, data):
        """ Here we expect the answer from the AI from a previous
        messageRoundtripToAI call """
        print("Got Data: ", data)
        print("Roundtrip message complete")
