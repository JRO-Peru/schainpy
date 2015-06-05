class ProcessCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:
    
        DATA:    Data Radar Object
        MESSAGE:       Data String
        STOP:    Event to Stop the process thread
        PAUSE:      Event to Pause the process thread
    """
    PROCESS, DATA, MESSAGE, STOP, PAUSE = range(5)
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class ClientCommand(object):
    """ A command to the client thread.
        Each command type has its associated data:
    
        CONNECT:    (host, port) tuple
        SEND:       Data string
        RECEIVE:    None
        CLOSE:      None
        PROCESS:    to processing
        SEND:       send a data
        SENDXML:    send xml file
    """
    CONNECT, SEND, SENDXML, RECEIVE, CLOSE, PROCESS = range(6)
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data


class ClientReply(object):
    """ A reply from the client thread.
        Each reply type has its associated data:
        
        ERROR:      The error string
        MESSAGE:    Data String
        DATA:        Data
        SUCCESS:    Depends on the command - for RECEIVE it's the received
                    data string, for others None.
    """
    ERROR, SUCCESS, MESSAGE, DATA= range(4)
    
    def __init__(self, type, data=None):
        self.type = type
        self.data = data
