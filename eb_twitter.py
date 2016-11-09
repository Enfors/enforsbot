import eb_thread, eb_message

import tweepy

import time

def read_private(filename):
    with open("private/" + filename, "r") as f:
        return f.read().replace('\n', '')
    
consumer_key    = read_private("consumer_key")
consumer_secret = read_private("consumer_secret")

access_token    = read_private("access_token")
access_token_secret = read_private("access_token_secret")

bot_screen_name = read_private("twitter_screen_name")

class TwitterThread(eb_thread.Thread):
        
    def run(self):
        super().run()
        with self.config.lock:
            self.config.twitter_auth = tweepy.OAuthHandler(consumer_key,
                                                           consumer_secret)
            self.config.twitter_auth.set_access_token(access_token,
                                                      access_token_secret)

        
        self.rest_thread = TwitterRestThread("TwitterRest",
                                             self.config)
        self.rest_thread.start()
        
        self.streams_thread = TwitterStreamsThread("TwitterStreams",
                                                   self.config)
        self.streams_thread.start()
        
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

        #self.send_direct_message("Bot running.", "enfors")
        
        while True:
            message = self.config.recv_message("TwitterRest")

            if message.msg_type == eb_message.MSG_TYPE_USER_MESSAGE:
                self.send_direct_message(message.data["text"],
                                         message.data["user"])
            elif message.msg_type == eb_message.MSG_TYPE_STOP_THREAD:
                self.stop()
                return


    def send_direct_message(self, message, user):
        with self.config.lock:
            self.api.update_status("D %s %s" % (user, message))
        
        

class TwitterStreamsThread(eb_thread.Thread):
    def __init__(self, name, config):
        super().__init__(name, config)
        
        self.listener = TweepyStreamListener()
        self.listener.set_config(config)
        self.stream = tweepy.Stream(auth = self.config.twitter_auth,
                                    listener = self.listener,
                                    timeout = 2)

        
    def run(self):
        super().run()
        message = eb_message.Message("TwitterStreams",
                                     eb_message.MSG_TYPE_THREAD_STARTED)
        self.config.send_message("Main", message)
        #self.stream.filter(track=['#svpol'])

        streaming = False
        
        while True:
            try:
                message = self.config.recv_message("TwitterStreams",
                                                   wait = False)
                if message and \
                   message.msg_type == eb_message.MSG_TYPE_STOP_THREAD:
                    self.stop()
                    return

                if not streaming:
                    self.stream.userstream(async = False)
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
                #print("Twitter: Exception handled: %s" % err)
                pass

        


class TweepyStreamListener(tweepy.StreamListener):

    def set_config(self, config):
        self.config = config
        
    
    def on_connect(self):
        #print("Streaming connection established.")
        pass

        
    def on_disconnect(self):
        print("Twitter: Streaming connection lost.")
        
    
    def on_status(self, status):
        return False


    def on_direct_message(self, status):
        text      = status.direct_message["text"]
        from_user = status.direct_message["sender"]["screen_name"]

        #print("TwitterStreams: Incoming message from %s: '%s'" %
        #      (from_user, text))

        if text.startswith("LocationUpdate"):
            #print("TwitterStreams: on_direct_message: LocationUpdate incoming")
            return self.on_location_update(from_user, text)

        if from_user == bot_screen_name:
            #print("TwitterStreams: Ignoring my own message: %s" % text)
            return True


        self.send_user_message_to_main(from_user, text)
        
        return True

    

    def on_location_update(self, from_user, text):
        if from_user != bot_screen_name and from_user != "Enfors":
            return False

        #print("on_location_update: text='%s', '%s'" % (text, text.replace("LocationUpdate ", "")))

        (location, arrived) = text.replace("LocationUpdate ", "").split(":")
        
        if arrived == "arrived":
            arrived = True
        else:
            arrived = False
        
        self.send_location_update_to_main(location, arrived)

    

    def send_user_message_to_main(self, user, text):
        message = eb_message.Message("TwitterStreams",
                                     eb_message.MSG_TYPE_USER_MESSAGE,
                                     { "user" : user, "text" : text })
        self.config.send_message("Main", message)



    def send_location_update_to_main(self, location, arrived):
        message = eb_message.Message("TwitterStreams",
                                     eb_message.MSG_TYPE_LOCATION_UPDATE,
                                     { "location" : location,
                                       "arrived"  : arrived })
        self.config.send_message("Main", message)
        


    def on_error(self, status_code):
        if status_code == 420:
            return False
