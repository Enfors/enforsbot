import threading, queue

class Config:
    def __init__(self):
        self.lock    = threading.Lock()

        self.threads = {
            "Twitter"     : None,
            "Telegram"    : None,
            "IRC"         : None
            }

        self.queues = {
            "Main"        : queue.Queue(),
            "TwitterRest" : queue.Queue(),
            "Telegram"    : queue.Queue(),
            "IRC"         : queue.Queue(),
            }
        
    def read_private(self, filename):
        with open("private/" + filename, "r") as f:
            return f.read().strip()
        

    def send_message(self, recipient, message):
        self.queues[recipient].put(message)


    def recv_message(self, recipient, wait = True):
        if wait:
            return self.queues[recipient].get()
        else:
            try:
                return self.queues[recipient].get_nowait()
            except queue.Empty:
                return None

