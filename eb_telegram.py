import eb_thread, eb_message

import telepot, random

def read_private(filename):
    with open("private/" + filename, "r") as f:
        return f.read().replace('\n', '')

TOKEN  = read_private("telegram_token")

bot_name = "Enfors_bot"

class TelegramThread(eb_thread.Thread):
    def __init__(self, config):
        super().__init__()
        
        self.config = config
        self.state = None # Temp. Remove later.

        
    def run(self):
        with self.config.lock:
            self.bot = telepot.Bot(TOKEN)

        self.bot.message_loop(self.handle_message)
            
        message = eb_message.Message("Telegram", eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)

        while True:
            message = self.config.recv_message("Telegram")

            if message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE:
                self.bot.sendMessage(message.data["user"], message.data["text"])

        


    def handle_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == "text":
            text = msg["text"].strip()
            user = msg["chat"]["id"]

            if text[0] == "/":
                text = text[1:]

            if text.lower().startswith("@enfors_bot "):
                text = text[12:]
            
            print("Telegram: Incoming message from %s: '%s'" %
                  (msg["from"]["first_name"], text))

            # If this is a kind of message only Telegram can handle
            # (inline keyboards, etc), then don't send it to the
            # main thread.
            if self.handle_telegram_message(text.lower(), user):
                return

            # Send the message to the main thread.
            message = eb_message.Message("Telegram",
                                         eb_message.MSG_TYPE_USER_MESSAGE,
                                         { "user": msg["chat"]["id"],
                                           "text": text })
            self.config.send_message("Main", message)
        else:
            print("Incoming %s message, ignoring.", content_type)



    def handle_telegram_message(self, text, user):
        if text == "rps": # Rock paper scissors
            self.state = "rps"

            show_keyboard = { "keyboard" : [[
                "rock", "paper", "scissors"
            ]]}
            
            self.bot.sendMessage(user, "You want to play "
                                 "rock, paper, scissors?\n"
                                 "Okay, make your choice:",
                            reply_markup = show_keyboard)

            return True

        if self.state == "rps" and text in [ "rock", "paper", "scissors" ]:
            self.finish_playing_rps(text, user)
            return True

        
        return False



    def finish_playing_rps(self, user_choice, user):
        my_choice = [ "rock", "paper", "scissors" ][random.randint(0, 2)]

        hide_keyboard = { "hide_keyboard" : True }
        self.bot.sendMessage(user, "I choose %s" % my_choice,
                             reply_markup = hide_keyboard)

        if ((my_choice == "rock" and user_choice == "paper") or
            (my_choice == "paper" and user_choice == "scissors") or
            (my_choice == "scissors" and user_choice == "rock")):
            self.bot.sendMessage(user, "You win!")
        else:
            self.bot.sendMessage(user, "I win!")
        
        self.state = None
        
