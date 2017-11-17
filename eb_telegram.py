import eb_message
import eb_thread

import random
import telepot
import time
import types


def read_private(filename):
    "Return contents of file in private/ dir."
    with open("private/" + filename, "r") as f:
        return f.read().replace('\n', '')


TOKEN = read_private("telegram_token")
bot_name = "Enfors_bot"


class TelegramThread(eb_thread.Thread):
    def __init__(self, name, config):
        super().__init__(name, config)

        self.state = None  # Temp. Remove later.

    def run(self):
        super().run()
        with self.config.lock:
            self.bot = telepot.Bot(TOKEN)

        try:
            self.bot.message_loop(self.handle_message)
        except:
            print("ERROR in telegram thread: bot.message_loop()")
            self.config.set_thread_state("Telegram", "exception")
            raise

        message = eb_message.Message("Telegram",
                                     eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)

        while True:
            try:
                message = self.config.recv_message("Telegram")

                if (message.msg_type == eb_message.MSG_TYPE_STOP_THREAD):
                    self.stop()
                    return

                if message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE:
                    self.send_message_to_user(message)
            except:
                print("ERROR in telegram thread")
                self.config.set_thread_state("Telegram", "exception")
                raise
                #time.sleep(60)

    def send_message_to_user(self, message):
        "Send a message to a user."

        choices = message.data["choices"]
        if choices:
            # If choices is like ["a", "b"], then we need to make it like
            # [["a", "b"]].
            if not isinstance(choices[0], list):
                choices = [choices]

            keyboard = {"keyboard": choices}
        else:
            keyboard = {"hide_keyboard": True}

        self.bot.sendMessage(message.data["user"],
                             message.data["text"],
                             reply_markup=keyboard)

    def handle_message(self, msg):
        "Take care of a message from the user."
        content_type, chat_type, chat_id = telepot.glance(msg)

        if content_type == "text":
            text = msg["text"].strip()
            user = msg["chat"]["id"]

            if text[0] == "/":
                text = text[1:]

            if text.lower().startswith("@enfors_bot "):
                text = text[12:]

            print("Telegram: Incoming message from %s(%d): '%s'" %
                  (msg["from"]["first_name"], user, text))

            # If this is a kind of message only Telegram can handle
            # (inline keyboards, etc), then don't send it to the
            # main thread.
            if self.handle_telegram_message(text.lower(), user):
                return

            # Send the message to the main thread.
            message = eb_message.Message("Telegram",
                                         eb_message.MSG_TYPE_USER_MESSAGE,
                                         {"user": msg["chat"]["id"],
                                          "text": text})
            self.config.send_message("Main", message)
        else:
            print("Incoming %s message, ignoring.", content_type)

    def handle_telegram_message(self, text, user):
        """Handle telegram-specific messages."""
        if text == "rps":  # Rock paper scissors
            self.state = "rps"

            show_keyboard = {"keyboard": [[
                "rock", "paper", "scissors"
            ]]}

            self.bot.sendMessage(user, "You want to play "
                                 "rock, paper, scissors?\n"
                                 "Okay, make your choice:",
                                 reply_markup=show_keyboard)

            return True

        if self.state == "rps" and text in ["rock", "paper", "scissors"]:
            self.finish_playing_rps(text, user)
            return True

        return False

    def finish_playing_rps(self, user_choice, user):
        """Finish a session of RPS."""
        my_choice = ["rock", "paper", "scissors"][random.randint(0, 2)]

        hide_keyboard = {"hide_keyboard": True}
        self.bot.sendMessage(user, "I choose %s" % my_choice,
                             reply_markup=hide_keyboard)

        if ((my_choice == "rock" and user_choice == "paper") or
            (my_choice == "paper" and user_choice == "scissors") or
            (my_choice == "scissors" and user_choice == "rock")):
            self.bot.sendMessage(user, "You win!")
        else:
            self.bot.sendMessage(user, "I win!")

        self.state = None
