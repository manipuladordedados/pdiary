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
import datetime
import configparser

USER_HOME = os.path.expanduser("~")
CONFIG_DIR_PATH = os.path.expanduser("~")+"/.config/pdiary/"

config = configparser.ConfigParser()
config.optionxform = str

class WriteFile(object):
    def toText(self, title, date, content):
        config.read(CONFIG_DIR_PATH+"pdiary.conf")
        with open(config.get("DEFAULT", "Export_Folder")+"/"+str(date)+"-"+title.replace(" ", "-").lower()+".txt", "w") as file:
            file.write(str(title)+"\n\n"+content+"\n\n"+datetime.datetime.strptime(str(date), '%Y-%m-%d').strftime("%B %d, %Y"))
            file.close()
