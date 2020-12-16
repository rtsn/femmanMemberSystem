#!/usr/bin/python
# -*- coding: utf-8 -*-


#import femmanEmail
import femmanDb
import logging

#import datetime
from datetime import *

from time import sleep
from random import randint

import sys
reload(sys)
sys.setdefaultencoding('utf8')


#This is the main module, containing the main function where all the
#modular components are combined. It also contains functions for
#generating membership html tables


def main():
    #this is where the magick happens
#    logFIleName = 'logs/femmanLog-{:%Y-%m-%d}'.format(datetime.now())
#    logging.basicConfig(filename=logFIleName,level=logging.DEBUG)

#    logging.debug('')
#    logging.debug('')
#    logging.debug('')
#    logging.debug('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
#    logging.debug('')
#    logging.debug('')
#    logging.debug('')

#    logging.debug('\n{:%Y-%m-%d %H:%M:%S} Summary script'.format(datetime.now()))
    database = "femman.db"
#    logging.debug('{:%Y-%m-%d %H:%M:%S} Create connection to db'.format(datetime.now()))
    conn = femmanDb.createConnection(database)

#    logging.debug('{:%Y-%m-%d %H:%M:%S} Fetch all members from db'.format(datetime.now()))
    members = femmanDb.getAllMembers(conn)

#    logging.debug('{:%Y-%m-%d %H:%M:%S} Create html table output for arr'.format(datetime.now()))
#    rowsToHtml(members)
#    logging.debug('{:%Y-%m-%d %H:%M:%S} Create html table output for admin'.format(datetime.now()))
#    rowsToHtmlAdmin(members)
    newMembers = []
    for member in members:
        member = list(member)
        memberDate = member[4]
        memberDate = datetime.strptime(memberDate,'%Y-%m-%d %H:%M:%S')
        compareDate = datetime.now() - timedelta(days=1)
        if memberDate >= compareDate:
            outputString = ""
            for item in member:
                outputString += str(item) + ","
            print outputString[:-2]

#        datetime_object = datetime_object - timedelta(days=1)

#    logging.debug('')
#    logging.debug('')
#    logging.debug('')
#    logging.debug('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
#    logging.debug('')
#    logging.debug('')
#    logging.debug('')


if __name__ == '__main__':
    main()
