"Twitter stuff for EnforsBot."

from __future__ import print_function

import time

import tweepy

import eb_thread
import eb_message

def read_private(filename):
    "Return the contents of a file in the private folder."
    with open("private/" + filename, "r") as f:
        return f.read().replace('\n', '')

CONSUMER_KEY = read_private("consumer_key")
CONSUMER_SECRET = read_private("consumer_secret")

ACCESS_TOKEN = read_private("access_token")
ACCESS_TOKEN_SECRET = read_private("access_token_secret")

BOT_SCREEN_NAME = read_private("twitter_screen_name")

class TwitterThread(eb_thread.Thread):
    "A Twitter thread."

    def __init__(self, name, config):
        super(TwitterThread, self).__init__(name, config)
        self.rest_thread = None
        self.streams_thread = None

    def run(self):
        super(TwitterThread, self).run()
        with self.config.lock:
            self.config.twitter_auth = tweepy.OAuthHandler(CONSUMER_KEY,
                                                           CONSUMER_SECRET)
            self.config.twitter_auth.set_access_token(ACCESS_TOKEN,
                                                      ACCESS_TOKEN_SECRET)


        self.rest_thread = TwitterRestThread("TwitterRest",
                                             self.config)
        self.rest_thread.start()

        #self.streams_thread = TwitterStreamsThread("TwitterStreams",
        #                                           self.config)
        #self.streams_thread.start()

        message = eb_message.Message("Twitter", eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)

        while True:
            message = self.config.recv_message("Twitter")

            if message.msg_type == eb_message.MSG_TYPE_STOP_THREAD:
                self.stop()
                return


class TwitterRestThread(eb_thread.Thread):
    def __init__(self, name, config):
        super().__init__(name, config)

        with self.config.lock:
            self.api = tweepy.API(self.config.twitter_auth)

    def run(self):
        super().run()
        message = eb_message.Message("TwitterRest",
                                     eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)

        while True:
            message = self.config.recv_message("TwitterRest")

            if message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE:
                self.send_direct_message(message.data["text"],
                                         message.data["user"])
            elif message.msg_type == eb_message.MSG_TYPE_STOP_THREAD:
                self.stop()
                return


    def send_direct_message(self, message, user):
        "Send the specified message as a Twitter direct message to user."
        with self.config.lock:
            self.api.update_status("D %s %s" % (user, message))



class TwitterStreamsThread(eb_thread.Thread):
    "The streams thread - used for input FROM Twitter."
    def __init__(self, name, config):
        super().__init__(name, config)

        self.listener = TweepyStreamListener()
        self.listener.set_config(config)
        self.stream = tweepy.Stream(auth=self.config.twitter_auth,
                                    listener=self.listener,
                                    timeout=60)

    def run(self):
        super().run()
        #last_err = None
        message = eb_message.Message("TwitterStreams",
                                     eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)
        #self.stream.filter(track=['#svpol'])

        streaming = False

        while True:
            try:
                message = self.config.recv_message("TwitterStreams",
                                                   wait=False)
                if message and \
                   message.msg_type == eb_message.MSG_TYPE_STOP_THREAD:
                    self.stop()
                    return

                if not streaming:
                    self.stream.userstream(async=False)
                    streaming = True

                time.sleep(1)

            except AttributeError as err:
                print("Twitter: Attribute exception handled: %s" % err)
            except ConnectionError as err:
                print("Twitter: Connection exception handled: %s" % err)
            except ValueError as err:
                print("Twitter: Value exception handled: %s" % err)
            except OSError as err:
                print("Twitter: OS exception handled: %s" % err)
            except Exception as err:
                # This happens every time it times out (a lot, intentionally)
                print("Twitter: Exception handled: %s" % err)
                #last_err = err



class TweepyStreamListener(tweepy.StreamListener):
    "Needed by TwitterStreamsThread."

    def __init__(self):
        super().__init__()
        self.config = None

    def set_config(self, config):
        "Set which config to use."
        self.config = config

    def on_connect(self):
        "What to do when the streams API connects."
        #print("Streaming connection established.")
        pass

    def on_disconnect(self):
        "What to do when disconnected."
        print("Twitter: Streaming connection lost.")

    def on_status(self, status):
        "What to do when a status message is received."
        return False


    def on_direct_message(self, status):
        "What to do when we receive a direct message."
        text = status.direct_message["text"]
        from_user = status.direct_message["sender"]["screen_name"]

        if text.startswith("LocationUpdate"):
            print("TwitterStreams: on_direct_message: LocationUpdate incoming")
            return self.on_location_update(from_user, text)

        if from_user.lower() == BOT_SCREEN_NAME.lower():
            return True

        print("TwitterStreams: Incoming message from %s: '%s' (%s)" %
              (from_user, text, BOT_SCREEN_NAME))

        self.send_user_message_to_main(from_user, text)
        return True

    def on_location_update(self, from_user, text):
        "What to do when we receive a location update."
        if from_user != BOT_SCREEN_NAME and from_user != "Enfors":
            return False

        print("on_location_update: text='%s', '%s'" %
              (text, text.replace("LocationUpdate ", "")))

        (location, arrived) = text.replace("LocationUpdate ", "").split(":")

        if arrived == "arrived":
            arrived = True
        else:
            arrived = False

        self.send_location_update_to_main(location, arrived)

    def send_user_message_to_main(self, user, text):
        "Send a user message to the main thread."
        message = eb_message.Message("TwitterStreams",
                                     eb_message.MSG_TYPE_USER_MESSAGE,
                                     {"user" : user, "text" : text})
        self.config.send_message("Main", message)

    def send_location_update_to_main(self, location, arrived):
        "Send a location update to the main thread."
        message = eb_message.Message("TwitterStreams",
                                     eb_message.MSG_TYPE_LOCATION_UPDATE,
                                     {"location" : location,
                                      "arrived" : arrived})
        self.config.send_message("Main", message)

    def on_error(self, status_code):
        "What to do on error."
        print("Twitter error: %d" % status_code)
        if status_code == 420:
            return False
