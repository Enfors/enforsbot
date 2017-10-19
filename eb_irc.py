# eb_irc.py by Christer Enfors

import datetime
import re
import sqlite3

import eb_message
import eb_thread

import botymcbotface.irc as irc

prev_msg_text = ""


class IRCThread(eb_thread.Thread, irc.IRCBot):

    def __init__(self, name, config):

        eb_thread.Thread.__init__(self, name, config)

        self.nickname = self.config.read_private("irc_nickname")
        self.password = self.config.read_private("irc_password")

        irc.IRCBot.__init__(self, self.nickname, self.password,
                            debug_level=0)

    def run(self):
        super().run()

        self.db = sqlite3.connect("enforsbot.db",
                                  detect_types=sqlite3.PARSE_DECLTYPES)

        self.connect("irc.freenode.net", "#Enfors")
        self.join_channel("#Enfors")

        message = eb_message.Message("IRC",
                                     eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)

        self.main_loop()

    def main_loop(self):
        "Main loop of the IRC thread."
        while True:

            # Check for messages from the main thread.
            message = self.config.recv_message("IRC", wait=False)

            if message:
                if (message.msg_type == eb_message.MSG_TYPE_STOP_THREAD):
                    self.send("QUIT :Bot stopped.")
                    self.get_msg(5)
                    self.stop()
                    return
                if (message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE):
                    # Send this message as a private message.
                    for line in message.data["text"].rstrip().split("\n"):
                        self.privmsg(message.data["user"], line)

            # Check for messages from IRC.
            msg = self.route_msg(1)

            if msg:
                self.log_irc_msg(msg)

    def on_private_msg(self, msg):
        self.debug_print("on_private_msg() called.", 2)
        # We don't need to respond to nickserv.
        if msg.sender.lower() == "nickserv":
            return None
        message = eb_message.Message("IRC",
                                     eb_message.MSG_TYPE_USER_MESSAGE,
                                     {"user": msg.sender,
                                      "msg_type": msg.msg_type,
                                      "channel": msg.channel,
                                      "text": msg.msg_text})
        self.config.send_message("Main", message)
            
    def on_channel_msg(self, msg):
        self.debug_print("on_channel_msg() called.", 2)
        
        global prev_msg_text

        match = re.search("^s/([^/]+)/([^/]*)/(g?)$",
                          msg.msg_text.strip())

        if match:
            old_text = match.group(1)
            new_text = match.group(2)
            self.privmsg(msg.channel, "Correction: %s" %
                         prev_msg_text.replace(old_text, new_text))
        else:
            prev_msg_text = msg.msg_text

    def on_join_msg(self, msg):
        self.debug_print("on_join_msg() called.", 2)

        self.debug_print("Transformed channel: '%s'" %
                         msg.channel.lower(), 3)
        
        if msg.channel.lower() != "#botymcbotface":
            return None

        self.debug_print("Transformed sender: '%s'" %
                         msg.sender.replace("@", "").lower(), 3)
        if msg.sender.replace("@", "").lower() in ["enfors",
                                                   "botymcbotface",
                                                   "botymctest",
                                                   "enforsbot",
                                                   "enforstestbot"]:
            if msg.sender.lower() != self.nickname.lower():
                self.make_operator(msg.channel, msg.sender)
            return None
            
        message = eb_message.Message("IRC",
                                     eb_message.MSG_TYPE_NOTIFY_USER,
                                     {"user": "enfors",
                                      "text": "We have a visitor in "
                                      "#BotyMcBotface: %s." % msg.sender})
        self.config.send_message("Main", message)

    def log_irc_msg(self, msg):
        "Log messages into the database."
        with self.config.lock, self.db:

            cur = self.db.cursor()

            cur.execute("insert into IRC_CHANNEL_LOG "
                        "(user, type, channel, message, time) values "
                        "(?, ?, ?, ?, ?)",
                        (msg.sender, msg.msg_type, msg.channel, msg.msg_text,
                         datetime.datetime.now()))
