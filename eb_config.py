import threading, queue

class Config:
    def __init__(self):
        self.lock    = threading.Lock()

        self.threads = {
            "Twitter"     : None,
            "Telegram"    : None,
            }

        self.queues = {
            "Main"        : queue.Queue(),
            "TwitterRest" : queue.Queue(),
            "Telegram"    : queue.Queue(),
            }
        

    def send_message(self, recipient, message):
        self.queues[recipient].put(message)


    def recv_message(self, recipient):
        return self.queues[recipient].get()
