#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3

con = sqlite3.connect("enforsbot.db")

with con:

    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS LOCATION_HISTORY("
                "USER        TEXT,"
                "LOCATION    TEXT,"
                "EVENT       TEXT,"
                "TIME        TIMESTAMP);")

    cur.execute("CREATE TABLE IF NOT EXISTS IRC_CHANNEL_LOG("
                "USER        TEXT,"
                "TYPE        TEXT,"
                "CHANNEL     TEXT,"
                "MESSAGE     TEXT,"
                "TIME        TIMESTAMP);")

    cur.execute("CREATE TABLE IF NOT EXISTS USER("
                "USERID      INTEGER PRIMARY KEY AUTOINCREMENT,"
                "NAME        TEXT,"
                "PASSWORD    TEXT,"
                "TWITTER_ID  TEXT,"
                "TELEGRAM_ID TEXT,"
                "IRC_ID      TEXT,"
                "CREATED     TIMESTAMP);")

