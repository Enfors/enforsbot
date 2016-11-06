# eb_irc.py by Christer Enfors

import time, re, sqlite3, datetime
import eb_thread, eb_message
import botymcbotface.irc as irc

prev_msg_text = ""

class IRCThread(eb_thread.Thread):

    def run(self):
        super().run()
        
        with (self.config.lock):
            self.nickname = self.config.read_private("irc_nickname")
            self.password = self.config.read_private("irc_password")
            self.db = sqlite3.connect("enforsbot.db",
                                      detect_types = sqlite3.PARSE_DECLTYPES)

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
                if (message.msg_type == eb_message.MSG_TYPE_STOP_THREAD):
                    self.stop()
                    return
                for line in message.data["text"].split("\n"):
                    self.bot.privmsg(message.data["user"],
                                     line.strip())

            # Check for messages from IRC.
            sender, msg_type, channel, msg_text = self.bot.get_msg(1)

            if sender or msg_type or channel or msg_text:
                self.handle_irc_message(sender, msg_type,
                                        channel, msg_text)


    def handle_irc_message(self, sender, msg_type, channel, msg_text):
        
        self.log_irc_message(sender, msg_type, channel, msg_text)

        if (msg_type == "PRIVMSG" and channel == self.nickname):
            self.handle_private_message(sender, msg_type, channel, msg_text)
            self.bot.debug_print("Private message: %s->%s: %s" % (sender,
                                                                  channel,
                                                                  msg_text))
            
            print("IRC: Incoming message from %s: '%s'" %
                  (sender, msg_text))

        if (msg_type == "PRIVMSG" and channel != self.nickname):
            self.bot.debug_print("Channel message: %s @ %s: %s" % (sender,
                                                                   channel,
                                                                   msg_text))
            self.handle_channel_message(sender, channel, msg_text)
            
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


    def handle_private_message(self, sender, msg_type, channel, msg_text):
        message = eb_message.Message("IRC",
                                     eb_message.MSG_TYPE_USER_MESSAGE,
                                     { "user"     : sender,
                                       "msg_type" : msg_type,
                                       "channel"  : channel,
                                       "text"     : msg_text })
        self.config.send_message("Main", message)

            
    def handle_channel_message(self, sender, channel, msg_text):
        global prev_msg_text

        match = re.search("^s/([^/]+)/([^/]*)/(g?)$",
                          msg_text.strip())

        if match:
            old_text = match.group(1)
            new_text = match.group(2)
            self.bot.privmsg(channel, "Correction: %s" %
                             prev_msg_text.replace(old_text, new_text))
        else:
            prev_msg_text = msg_text

    def log_irc_message(self, sender, msg_type, channel, text):

        with self.config.lock, self.db:

            cur = self.db.cursor()

            cur.execute("insert into IRC_CHANNEL_LOG "
                        "(user, type, channel, message, time) values "
                        "(?, ?, ?, ?, ?)",
                        (sender, msg_type, channel, text,
                        datetime.datetime.now()))
            
