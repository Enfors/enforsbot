# eb_irc.py by Christer Enfors

import eb_thread, eb_message
import botymcbotface.irc as irc

class IRCThread(eb_thread.Thread):

    def __init__(self, config):
        super().__init__()

        self.config = config


    def run(self):
        
        with (self.config.lock):
            self.nickname = self.config.read_private("irc_nickname")
            self.password = self.config.read_private("irc_password")

        self.bot = irc.IRCBot(self.nickname, self.password, debug = False)

        self.bot.connect("irc.freenode.net", "#BotyMcBotface")

        message = eb_message.Message("IRC",
                                     eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)
        
        self.main_loop()


    def main_loop(self):

        while True:

            # Check for messages from the main thread.
            message = self.config.recv_message("IRC", wait = False)

            if message:
                self.bot.privmsg(message.data["user"],
                                 message.data["text"])

            # Check for messages from IRC.
            sender, msg_type, channel, msg_text = self.bot.get_msg(1)

            if sender or msg_type or channel or msg_text:
                self.handle_irc_message(sender, msg_type,
                                        channel, msg_text)


    def handle_irc_message(self, sender, msg_type, channel, msg_text):
        
        if (msg_type == "PRIVMSG" and channel == self.nickname):
            self.bot.debug_print("Private message: %s->%s: %s" % (sender,
                                                                  channel,
                                                                  msg_text))
            
            print("IRC: Incoming message from %s: '%s'" %
                  (sender, msg_text))
            
            message = eb_message.Message("IRC",
                                         eb_message.MSG_TYPE_USER_MESSAGE,
                                         { "user": sender.replace("@", ""),
                                           "text": msg_text })
            self.config.send_message("Main", message)
            
            
        if (msg_type == "PRIVMSG" and channel != self.nickname):
            self.bot.debug_print("Channel message: %s @ %s: %s" % (sender,
                                                                   channel,
                                                                   msg_text))
            
        if (msg_type == "JOIN" and channel.lower() == "#botymcbotface"):

            if (sender.replace("@", "").lower() in [ "enfors",
                                                     "botymcbotface",
                                                     "botymctest",
                                                     "enforsbot"]):
                return None
            
            message = eb_message.Message("IRC",
                                         eb_message.MSG_TYPE_NOTIFY_USER,
                                         { "user": "enfors",
                                           "text": "We have a visitor in " \
                                           "#BotyMcBotface: %s." % sender})
            self.config.send_message("Main", message)
                                           
