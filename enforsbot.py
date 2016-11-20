#!/usr/bin/env python3
"enforsbot.py by Christer Enfors (c) 2015, 2016"
from __future__ import print_function

import datetime
import re
import socket
import subprocess
import sqlite3

import eb_config
import eb_message
import eb_twitter
import eb_telegram
import eb_irc

#twitter_thread = eb_twitter.TwitterThread()

SYSCOND_DIR = "/home/enfors/syscond"


class EnforsBot(object):
    "The main class of the application."

    def __init__(self):
        self.config = eb_config.Config()

        # Responses are regexps.
        self.responses = {
            "ip"                 : self.respond_ip,
            "what.* ip .*"       : self.respond_ip,
            "what.*address.*"    : self.respond_ip,
            "ping"               : "Pong.",
            ".*good morning.*"   : "Good morning!",
            ".*good afternoon.*" : "Good afternoon!",
            ".*good evening.*"   : "Good evening!",
            ".*good night.*"     : "Good night!",
            "thank.*"            : "You're welcome.",
            "test"               : "I am running and connected.",
            "hello"              : "Hello there!",
            "hi"                 : "Hi there!",
            "LocationUpdate .*"  : self.handle_incoming_location_update,
            "locate"             : self.respond_location,
            "syscond"            : self.respond_syscond,
            "status"             : self.respond_status,
        }

        # Incoming user messages can come from several different threads.
        # When we get one, we keep track of which thread it's from, so
        # we know which thread we should send the response to. For example,
        # if we get a user message from TwitterStream, we should send the
        # response to TwitterRest.

        self.response_threads = {
            #Incoming from     Send response to
            #===============   ================
            "TwitterStreams" : "TwitterRest",
            "Telegram"       : "Telegram",
            "IRC"            : "IRC"
        }

        self.location = None
        self.arrived = False

        self.database = sqlite3.connect("enforsbot.db",
                                        detect_types=sqlite3.PARSE_DECLTYPES)



    def start(self):
        "Start the bot."
        self.start_all_threads()

        self.main_loop()


    def main_loop(self):
        "The main loop of the bot."
        try:
            while True:
                message = self.config.recv_message("Main")

                print("Main: Incoming message from thread %s..." % \
                      message.sender)

                if message.msg_type == \
                   eb_message.MSG_TYPE_THREAD_STARTED:
                    print("Thread started: %s" % message.sender)
                    self.config.set_thread_state(message.sender,
                                                 "running")

                elif message.msg_type == eb_message.MSG_TYPE_THREAD_STOPPED:
                    print("Thread stopped: %s" % message.sender)
                    self.config.set_thread_state(message.sender,
                                                 "stopped")

                elif message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE:
                    self.handle_incoming_user_message(message, \
                                        self.response_threads[message.sender])

                elif message.msg_type == eb_message.MSG_TYPE_LOCATION_UPDATE:
                    self.handle_incoming_location_update(message)

                elif message.msg_type == eb_message.MSG_TYPE_NOTIFY_USER:
                    self.handle_incoming_notify_user(message)
                else:
                    print("Unsupported incoming message type: %d" % \
                          message.msg_type)
        except (KeyboardInterrupt, SystemExit):
            self.stop_all_threads()
            return


    def start_all_threads(self):
        "Start all necessary threads."
        with self.config.lock:

            twitter_thread = eb_twitter.TwitterThread("Twitter",
                                                      self.config)
            self.config.threads["Twitter"] = twitter_thread

            telegram_thread = eb_telegram.TelegramThread("Telegram",
                                                         self.config)
            self.config.threads["Telegram"] = telegram_thread

            irc_thread = eb_irc.IRCThread("IRC", self.config)
            self.config.threads["IRC"] = irc_thread

        self.config.set_thread_state("Twitter", "starting")
        twitter_thread.start()

        self.config.set_thread_state("Telegram", "starting")
        telegram_thread.start()

        self.config.set_thread_state("IRC", "starting")
        irc_thread.start()


    def stop_all_threads(self):
        "Stop all threads."
        print("") # Add a newline to get away from "^C" on screen

        with self.config.lock:

            threads_to_stop = [thread for thread in self.config.threads if
                               self.config.thread_states[thread] == "running"]

            print("Stopping threads: %s" % threads_to_stop)

        for thread in threads_to_stop:
            if thread not in self.config.threads:
                print("ERROR: %s not in self.config.threads!" % thread)
            self.stop_thread(thread)

        print("ALL THREADS STOPPED.")


    def stop_thread(self, thread):
        "Stop one specific thread."
        message = eb_message.Message("Main",
                                     eb_message.MSG_TYPE_STOP_THREAD, {})
        self.config.send_message(thread, message)

        self.config.threads[thread].join()


    def handle_incoming_user_message(self, message, response_thread):
        "Hande an incoming message of type USER."
        user = message.data["user"]
        text = message.data["text"]

        #print("Main: Message from %s: '%s'" % (user, text))

        used_response = None
        default_response = "I'm afraid I don't understand."

        # If this is an IRC message:
        if response_thread == "IRC":
            #msg_type = message.data["msg_type"]
            channel = message.data["channel"]

            # But don't respond unless it's a private message.
            if channel.lower() != "enforsbot" and \
               channel.lower() != "enforstestbot":
                return None

            # We should't try to respond to NickServ.
            if user.lower() == "nickserv":
                return None

        text = text.lower()

        for pattern, response in self.responses.items():
            pat = re.compile(pattern)

            if pat.match(text):
                used_response = response

                if callable(used_response):
                    used_response = used_response(text)

        if used_response is None:
            used_response = default_response

        used_response = used_response.strip() + "\n"
        if used_response is not None:
            message = eb_message.Message("Main",
                                         eb_message.MSG_TYPE_USER_MESSAGE,
                                         {"user" : user,
                                          "text" : used_response})
            self.config.send_message(response_thread, message)


    def respond_ip(self, message):
        "Return our local IP address."
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("gmail.com", 80)) # I'm abusing gmail.
                                        # I'm sure it can take it.
        response = "I'm currently running on IP address %s." % \
                   sock.getsockname()[0]
        sock.close()

        return response


    def handle_incoming_location_update(self, message):
        "Handle incoming request for our location."
        user = "Enfors" # Hardcoded for now. Sue me.
        location = message.data["location"]
        arrived = message.data["arrived"]

        print("Updating location: [%s:%s]" % (location, str(arrived)))

        with self.config.lock, self.database:

            cur = self.database.cursor()

            if arrived:

                self.location = location
                self.arrived = True

                cur.execute("insert into LOCATION_HISTORY "
                            "(user, location, event, time) values "
                            "(?, ?, 'arrived', ?)",
                            (user, location, datetime.datetime.now()))

                print("Main: Location updated: %s" % self.location)

            else: # if leaving

                # If leaving the location I'm currently at (sometimes
                # the "left source" message arrives AFTER "arrived at
                # destination" message), skipping those.
                if self.arrived is False or location == self.location:

                    cur.execute("insert into LOCATION_HISTORY "
                                "(user, location, event, time) values "
                                "(?, ?, 'left', ?)",
                                (user, location, datetime.datetime.now()))

                    print("Main: Location left: %s" % location)
                    self.arrived = False

        return None


    def handle_incoming_notify_user(self, message):
        "Send notification message through Twitter."

        out_message = eb_message.Message("Main",
                                         eb_message.MSG_TYPE_USER_MESSAGE,
                                         {"user": message.data["user"],
                                          "text": message.data["text"]})
        self.config.send_message("TwitterRest", out_message)


    def respond_location(self, message):
        "Return our location."
        #if not self.location:
        #    return "There whereabouts of Enfors are currently unknown."

        #if self.arrived:
        #    return "Enfors was last seen arriving at %s." % self.location
        #else:
        #    return "Enfors was last seen leaving %s."     % self.location

        with self.database:

            cur = self.database.cursor()

            cur.execute("select * from LOCATION_HISTORY "
                        "order by ROWID desc limit 1")

            try:
                (user, location, event, timestamp) = cur.fetchone()
            except TypeError:
                return "I have no information on that."

            if event == "arrived":
                return "%s %s at %s %s." % (user, event, location, \
                    self.get_datetime_diff_string(timestamp,
                                                  datetime.datetime.now()))
            else:
                return "%s %s %s %s." % (user, event, location, \
                    self.get_datetime_diff_string(timestamp,
                                                  datetime.datetime.now()))


    def respond_syscond(self, message):
        "Return the SysCond status of the host."
        return self.check_syscond()


    def respond_status(self, message):
        "Return threads status."
        output = ""

        for thread in self.config.threads:
            output += "%s: %s\n" % (thread,
                                    self.config.get_thread_state(thread))

        return output


    def check_syscond(self):
        "Check the SysCond status of the host."
        try:
            syscond_output = subprocess.Popen(["syscond", "status", "-n"], \
                stdout=subprocess.PIPE).communicate()[0]

            return syscond_output.decode("utf-8")
        except FileNotFoundError:
            return "SysCond is not installed on this host."


    def get_datetime_diff_string(self, date1, date2):
        "Return the diff between two datetimes, in short format."
        if date1 > date2:
            return "in the future"

        diff = date2 - date1

        total_seconds = diff.total_seconds()

        minutes = total_seconds // 60
        hours = total_seconds // 60 // 60
        days = total_seconds // 60 // 60 // 24

        if days:
            hours -= (days * 24)

            return "%d %s, %d %s ago" % (days,
                                         self.get_possible_plural("day", days),
                                         hours,
                                         self.get_possible_plural("hour",
                                                                  hours))
        elif hours:
            minutes -= (hours * 60)

            return "%d %s, %d %s ago" % (hours,
                                         self.get_possible_plural("hour",
                                                                  hours),
                                         minutes,
                                         self.get_possible_plural("minute",
                                                                  minutes))

        elif minutes:
            return "%d %s ago" % (minutes, self.get_possible_plural("minute",
                                                                    minutes))

        else:
            return "just now"


    def get_possible_plural(self, word, num):
        "Return word+s if num is plural, otherwise word."
        if num == 1:
            return word
        else:
            return word + "s"


def main():
    "Start the application."
    app = EnforsBot()
    app.start()


if __name__ == "__main__":
    main()
