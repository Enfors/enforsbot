MSG_TYPE_THREAD_STARTED     = 1
MSG_TYPE_USER_MESSAGE       = 2
MSG_TYPE_LOCATION_UPDATE    = 3
MSG_TYPE_NOTIFY_USER        = 4

VALID_MSG_TYPES = [
    MSG_TYPE_THREAD_STARTED,
    MSG_TYPE_USER_MESSAGE,
    MSG_TYPE_LOCATION_UPDATE,
    MSG_TYPE_NOTIFY_USER,
    ]

example_user_messages_data= {
    # Incoming or outgoing depends on the context. Could be from owner to bot or
    # bot to owner (or perhaps from bot to other user)
    "user" : "username",
    "text" : "foo",
}

example_location_update_data = {
    "location" : "home",
    "arrived"  : True, # True = arrived, False = left
}

class MessageTypeInvalid(Exception):
    pass

class Message:
    def __init__(self, sender, msg_type, data = None):

        if msg_type not in VALID_MSG_TYPES:
            raise MessageTypeInvalid
        
        self.sender   = sender
        self.msg_type = msg_type
        self.data     = data

    def __repr__(self):
        return "Message type: %d, sender: %s" % (self.msg_type, self.sender)
        

    
