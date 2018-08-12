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
import sys
from fcntl import lockf, LOCK_EX, LOCK_NB
from pdiary.forms import App

# This prevent several instances of pdiary running at the same time
class SingleInstance(object):
    def __init__(self):
        fd = os.open("/tmp/pdiary.lock", os.O_WRONLY | os.O_CREAT | os.O_TRUNC)
        try:
           lockf(fd, LOCK_EX | LOCK_NB)
        except IOError:
          print("An Instance of pdiary is already running.")
          sys.exit(1)

def main():
  try:
    MyApp = App()
    SingleInstance()
    MyApp.run()
  except (KeyboardInterrupt):
    exit()