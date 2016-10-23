#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys

con = sqlite3.connect("enforsbot.db")

with con:

    cur = con.cursor()
    cur.execute("CREATE   TABLE LOCATION_HISTORY("
                "USER     TEXT,"
                "LOCATION TEXT,"
                "EVENT    TEXT,"
                "TIME      TIMESTAMP);")
    

                
