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

        self.bot = irc.IRCBot(self.nickname, self.password, debug_level = 1)

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
                    self.bot.send("QUIT :Bot stopped.")
                    self.bot.get_msg(5)
                    self.stop()
                    return
                if (message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE):
                    # Send this message as a private message.
                    for line in message.data["text"].rstrip().split("\n"):
                        self.bot.privmsg(message.data["user"], line)

            # Check for messages from IRC.
            msg = self.bot.get_msg(1)

            if not msg:         # If timed out
                continue
            
            self.handle_irc_message(msg)


    def handle_irc_message(self, msg):
        
        self.log_irc_message(msg)

        if (msg.msg_type == "PRIVMSG" and msg.channel == self.nickname):
            self.handle_private_message(msg)
            self.bot.debug_print("Private message: %s->%s: %s" % (msg.sender,
                                                                  msg.channel,
                                                                  msg.msg_text),
                                 1)
            
            print("IRC: Incoming message from %s: '%s'" %
                  (msg.sender, msg.msg_text))

        if (msg.msg_type == "PRIVMSG" and msg.channel != self.nickname):
            self.bot.debug_print("Channel message: %s @ %s: %s" % (msg.sender,
                                                                   msg.channel,
                                                                   msg.msg_text),
                                 1)
            self.handle_channel_message(msg)
            
        if (msg.msg_type == "JOIN" and
            msg.channel.lower() == "#botymcbotface"):

            if (msg.sender.replace("@", "").lower() in [ "enfors",
                                                         "botymcbotface",
                                                         "botymctest",
                                                         "enforsbot"]):
                return None
            
            message = eb_message.Message("IRC",
                                         eb_message.MSG_TYPE_NOTIFY_USER,
                                         { "user": "enfors",
                                           "text": "We have a visitor in " \
                                           "#BotyMcBotface: %s." % msg.sender})
            self.config.send_message("Main", message)


    def handle_private_message(self, msg):
        message = eb_message.Message("IRC",
                                     eb_message.MSG_TYPE_USER_MESSAGE,
                                     { "user"     : msg.sender,
                                       "msg_type" : msg.msg_type,
                                       "channel"  : msg.channel,
                                       "text"     : msg.msg_text })
        self.config.send_message("Main", message)

            
    def handle_channel_message(self, msg):
        global prev_msg_text

        match = re.search("^s/([^/]+)/([^/]*)/(g?)$",
                          msg.msg_text.strip())

        if match:
            old_text = match.group(1)
            new_text = match.group(2)
            self.bot.privmsg(msg.channel, "Correction: %s" %
                             prev_msg_text.replace(old_text, new_text))
        else:
            prev_msg_text = msg.msg_text
            

    def log_irc_message(self, msg):

        with self.config.lock, self.db:

            cur = self.db.cursor()

            cur.execute("insert into IRC_CHANNEL_LOG "
                        "(user, type, channel, message, time) values "
                        "(?, ?, ?, ?, ?)",
                        (msg.sender, msg.msg_type, msg.channel, msg.msg_text,
                        datetime.datetime.now()))
            
