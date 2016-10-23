#!/usr/bin/env python3

import sys, time, telepot

TOKEN = "215732138:AAE-wr0nphxECqJkOxbgcHrg7QlWRksoWJo"

def handle_incoming_msg(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)
    print(content_type, chat_type, chat_id)

    if content_type == "text":
        print("Text: %s" % msg["text"])

        user_id = msg["chat"]["id"]
        print("Message was from user_id %s." % user_id)
        bot.sendMessage(user_id, "Hello World!")

        show_keyboard = {"keyboard": [["Yes", "No"], ["Maybe", "Maybe not"]]}
        bot.sendMessage(user_id, "This is a custom keyboard", reply_markup=show_keyboard)

        hide_keyboard = {"hide_keyboard": True}
        bot.sendMessage(user_id, "I am hiding it", reply_markup=hide_keyboard)


bot = telepot.Bot(TOKEN)
bot.message_loop(handle_incoming_msg)
print("Listening...")

# Keep the program running
while True:
    time.sleep(10)
