import threading, queue

class Config:
    def __init__(self):
        self.lock    = threading.Lock()

        self.threads = {
            "Twitter"        : None,
            "TwitterRest"    : None,
            "TwitterStreams" : None,
            "Telegram"       : None,
            "IRC"            : None
            }

        self.queues = {
            "Main"           : queue.Queue(),
            "Twitter"        : queue.Queue(),
            "TwitterRest"    : queue.Queue(),
            "TwitterStreams" : queue.Queue(),
            "Telegram"       : queue.Queue(),
            "IRC"            : queue.Queue(),
            }

        self.thread_states = { }

        for thread in self.threads:
            self.thread_states[thread] = "stopped"

            
    def read_private(self, filename):
        with open("private/" + filename, "r") as f:
            return f.read().strip()

        
    def set_thread_state(self, thread, state):
        with self.lock:
            self.thread_states[thread] = state
            return True


    def get_thread_state(self, thread):
        with self.lock:
            return self.thread_states[thread]
        

    def send_message(self, recipient, message):
        if (recipient not in self.queues):
            print("send_message(): No such recipient: %s" % recipient)
            return None
        self.queues[recipient].put(message)


    def recv_message(self, recipient, wait = True):
        if wait:
            return self.queues[recipient].get()
        else:
            try:
                return self.queues[recipient].get_nowait()
            except queue.Empty:
                return None

