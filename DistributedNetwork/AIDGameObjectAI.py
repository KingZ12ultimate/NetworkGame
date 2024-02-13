from direct.distributed.DistributedObjectAI import DistributedObjectAI


class AIDGameObjectAI(DistributedObjectAI):
    def __init__(self, ai_repository):
        DistributedObjectAI.__init__(self, ai_repository)

    def message_roundtrip_to_ai(self, data):
        """ The client sent us some data to process.  So work with it and send
        changed data back to the requesting client """
        requester_id = self.air.getAvatarIdFromSender()
        print("Got client data: ", data, " from client with ID ", requester_id)

        ai_changed_data = (
            data[0] + " from the AI",
            data[1] + 1,
            data[2])

        print("Sending modified game data back: ", ai_changed_data)
        self.d_message_roundtrip_to_client(ai_changed_data, requester_id)

    def d_message_roundtrip_to_client(self, data, requester_id):
        """ Send the given data to the requesting client """
        print("Send message to back to: ", requester_id)
        self.sendUpdateToAvatarId(requester_id, "message_roundtrip_to_client", [data])
