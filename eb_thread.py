import threading

import eb_message

class Thread(threading.Thread):

    def __init__(self, name, config):
        super().__init__()
        self.name   = name
        self.config = config

    def run(self):
        with self.config.lock:
            self.config.threads[self.name] = self
        
    
    def stop(self):

        print("Thread stopped: %s" % self.name)
        message = eb_message.Message("Main",
                                     eb_message.MSG_TYPE_THREAD_STOPPED, { } )
        self.config.send_message(self.name, message)

