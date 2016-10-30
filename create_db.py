#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

con = sqlite3.connect("enforsbot.db")

with con:

    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS LOCATION_HISTORY("
                "USER     TEXT,"
                "LOCATION TEXT,"
                "EVENT    TEXT,"
                "TIME     TIMESTAMP);")

    cur.execute("CREATE TABLE IF NOT EXISTS IRC_CHANNEL_LOG("
                "USER     TEXT,"
                "TYPE     TEXT,"
                "CHANNEL  TEXT,"
                "MESSAGE  TEXT,"
                "TIME     TIMESTAMP);")
