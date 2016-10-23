# EnforsBot - a Twitter / Telegram bot

EnforsBot is a small bot I run on my Raspberry Pi. It doesn't have
that many features, but it does some things that are useful to me:

- It allows me to ask it questions via Twitter or Telegram.
- It can tell me which IP address it has, which is sometimes useful
  when its host (typically my Raspberry Pi) is using DHCP, and I don't
  know which IP address it currently has.
- I have a number of IFTTT recipes set up which tells this bot when I
  (read: my phone) enter and leave certain locations. This bot then
  keeps track of this information, which makes it possible for a
  certain set of white-listed people to ask it where I am.
- It has a monitoring function which can tell me how the host it's
  running on is doing, if it's low on disc space or under heavy load,
  if last night's backup failed, etc. This is based on the syscond
  package with is also on my Github account.
  
# Setting it up

To run this bot, you need certain files to be put into a directory
called "private" inside the enforsbot directory. These files uniquely
identifies the bot to Twitter and Telegram, which means I can't put
them on Github (because then people would be able to run the bot *with
the same name*, which wouldn't work). Therefore, if you want to run
this bot, you'll have to get your *own* versions of these files, and
then run the bot under a different name. These files are as follows:

For Twitter:
- private/consumer_key
- private/consumer_secret
- private/access_token
- private/access_token_secret

For Telegram:
- private/telegram_token

You can get your own versions of these files by creating a bot at
twitter.com and telegram.com, respectively.
