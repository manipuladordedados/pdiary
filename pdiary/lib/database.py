#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Copyright (C) 2018 Valter Nazianzeno <manipuladordedados at gmail dot com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import configparser
import peewee
from playhouse.sqlcipher_ext import SqlCipherDatabase
from playhouse.sqlite_ext import SqliteExtDatabase, FTSModel

# Default directory for config files and db file
CONFIG_DIR_PATH = os.path.expanduser("~")+"/.config/pdiary/"
DB_FILE = CONFIG_DIR_PATH+"data.db"

# Load configuration file
config = configparser.ConfigParser()
config.read(CONFIG_DIR_PATH+"pdiary.conf")

database_proxy = peewee.DatabaseProxy()

# Main tables
class Entry(peewee.Model):
    title = peewee.TextField()
    date = peewee.TextField()
    content = peewee.TextField()

    class Meta:
        database = database_proxy

class FTSEntry(FTSModel):
    content = peewee.TextField()

    class Meta:
        database = database_proxy

class dbManager(object):
    def __init__(self, password=None):
        # Create the config folder if it doesn't already exists
        if not os.path.exists(CONFIG_DIR_PATH):
            os.mkdir(CONFIG_DIR_PATH)
        # If password option is selected initalize the DB
        if password != None:
            database = SqlCipherDatabase(None)
            database_proxy.initialize(database)
            database.init(DB_FILE, passphrase=password, pragmas={'kdf_iter':64000})
        # Password option not selected
        else:
            database = peewee.SqliteDatabase(None)
            database_proxy.initialize(database)
            database.init(DB_FILE)
        # Create tables for the main entries and searches
        database.create_tables([Entry])
        database.create_tables([FTSEntry])

    def add(self, t, d, c):
        Entry.create(title=t, date=d, content=c)
        FTSEntry.create(content="\n".join((t, c)))

    def resultado(self, term):
        query = (Entry.select()
            .join(FTSEntry, on=(Entry.id == FTSEntry.docid))
            .where(FTSEntry.match(term)))
        if query.exists():
            return True
        else:
            return False

    def view(self, _id):
        # Create a list with each item's ids, the content stored in the database
        # is based on the position of these ids.
        ids = [pk.id for pk in Entry.select(Entry.id)]
        query = Entry.select().where(Entry.id == ids[_id])
        for q in query:
            return q.id, q.title, q.date, q.content

    def list_entries(self):
        entries_list = []
        for entry in Entry.select(Entry.title, Entry.date):
            entries_list.append(entry.date + " "*5 + entry.title)
        return entries_list

    def list_searched_entries(self, term):
        searched_entries = []
        query = (Entry.select()
            .join(FTSEntry, on=(Entry.id == FTSEntry.docid))
            .where(FTSEntry.match(term)))
        for entry in query:
            searched_entries.append(entry.date + " "*5 + entry.title)
        return searched_entries

    def search_entries(self, term):
        entries_list = []
        for entry in Entry.select(Entry.title):
            if  entry.title == "Ola":
                entries_list.append(entry.title)
        return entries_list

    def edit(self, _id, title, date, content):
        entry = Entry.get(Entry.id == self.view(_id)[0])
        entry.title = title
        entry.date = date
        entry.content = content
        entry.save()

    def remove(self, _id):
        entry = Entry.get(Entry.id == self.view(_id)[0])
        entry.delete_instance()
