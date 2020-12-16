#!/usr/bin/python
# -*- coding: utf-8 -*-

import femmanEmail
import femmanDb
import femmanMisc
import logging

#import datetime
from datetime import *

from time import sleep
from random import randint

import os
import sys
from importlib import reload #py3 conv
reload(sys)
#sys.setdefaultencoding('utf8') #py3 conv

def main():

    #this is where the magick happens
    logFIleName = 'logs/femmanLog-{:%Y-%m-%d}'.format(datetime.now())
    logging.basicConfig(filename=logFIleName,level=logging.DEBUG)
    #start logging

    logging.debug('')
    logging.debug('')

    logging.debug('{:%Y-%m-%d %H:%M:%S} Generating HTML output'.format(datetime.now()))
    logging.debug('{:%Y-%m-%d %H:%M:%S} Create outputs'.format(datetime.now()))

    database = "femman.db"
    logging.debug('{:%Y-%m-%d %H:%M:%S} Create connection to db'.format(datetime.now()))
    conn = femmanDb.createConnection(database)

    logging.debug('{:%Y-%m-%d %H:%M:%S} Fetch all members from db'.format(datetime.now()))
    members = femmanDb.getAllMembers(conn)

    logging.debug('{:%Y-%m-%d %H:%M:%S} Create html table output for arr'.format(datetime.now()))
    femmanMisc.rowsToHtml(members)
    logging.debug('{:%Y-%m-%d %H:%M:%S} Create html table output for admin'.format(datetime.now()))
    femmanMisc.rowsToHtmlAdmin(members)


    print(members)

if __name__ == '__main__':
    main()
