# -*- coding: utf-8 -*-
"""
    Copyright © 2019 Galyfray
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this module.  If not, see <https://www.gnu.org/licenses/>.
"""

__author__="Galyfray"

import os
import datetime

def f_open(path:str):
    if os.path.exists(path):
        fichier = open(path,"a")
    else:
        fichier=open(path,"w")
    return fichier

class logger(object):

    def __init__(self):
        pass

    @staticmethod
    def log(logType:str,logs:str):

        fichier = f_open(logType + ".log")

        logs = "[" + datetime.datetime.now().isoformat(sep=' ',timespec='seconds') + "]" + logs

        if not(logs.endswith("\n")):
            logs=logs + "\n"
        fichier.write(logs)

    def write(self,data):
        logger.log("global",data)