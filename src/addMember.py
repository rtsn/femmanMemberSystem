#!/usr/bin/python3
# -*- coding: utf-8 -*-

#manually add a member from command line

import femmanEmail
import femmanDb
import logging

from datetime import *

from time import sleep
from random import randint

import os
import sys
from importlib import reload #py3 conv
reload(sys)


def main():

    logFIleName = 'logs/femmanLog-{:%Y-%m-%d}'.format(datetime.now())
    logging.basicConfig(filename=logFIleName,level=logging.DEBUG)

    logging.debug('')

    logging.debug('{:%Y-%m-%d %H:%M:%S} Manually adding member via commandline'.format(datetime.now()))

    name = input("name: ").encode('utf-8') #assume prefName == Name
    email = input("email: ")
    email = email.lower()
    email = email.strip()
    now = datetime.now()
    memberDate = now.strftime("%Y-%m-%d %H:%M:00")

    member = [name,name,email,memberDate]

    database = "femman.db"

    # create a database connection
    logging.debug('{:%Y-%m-%d %H:%M:%S} Create connection to db'.format(datetime.now()))
    conn = femmanDb.createConnection(database)
    conn.text_factory = str

    sqlCreateMembersTable= """ CREATE TABLE IF NOT EXISTS members%s(
                                        id integer PRIMARY KEY,
                                        fullName text NOT NULL,
                                        prefName text NOT NULL,
                                        email    text NOT NULL,
                                        [MemberDate] timestamp NOT NULL
                                    ); """ %

    with conn:

        # create members table table if it doesn't exist, i.e. first
        # time running program

        logging.debug('{:%Y-%m-%d %H:%M:%S} Creating table'.format(datetime.now()))
        femmanDb.createTable(conn, sqlCreateMembersTable)


        logging.debug('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())+str(member))
        if femmanDb.isMember(conn, member) == True:
            logging.debug('{:%Y-%m-%d %H:%M:%S} Already member'.format(datetime.now()))
            outputString = str(member)+ " already a member"
            print(outputString)
            sys.exit()


        print("Adding member to database...")
        logging.debug('{:%Y-%m-%d %H:%M:%S} Adding member to db'.format(datetime.now()))
        memberNumber = femmanDb.insertMember(conn, tuple(member))
        strDate = str(member[3])
        print(" "*8 + "Nr: "+ str(memberNumber)+" ("+strDate+")")
        print(" "*8 +member[0].decode('utf-8'))
        print(" "*8 +member[2])
        logging.debug('{:%Y-%m-%d %H:%M:%S} added to db with nr'.format(datetime.now())+str(memberNumber))

        print("    Adding member to moosend")
        moosendResult = femmanEmail.moosend(member)
        if moosendResult != 0:
            print("See error above. Add manually. Important!")
        else:
            print("    ok!")

        print("    Emailing welcome msg...")
        logging.debug('{:%Y-%m-%d %H:%M:%S} Email welcome msg'.format(datetime.now()))
        member[3] = datetime.now()
        femmanEmail.sendEmail([memberNumber]+member)


#   logging.debug('{:%Y-%m-%d %H:%M:%S} Create outputs'.format(datetime.now()))

#   database = "femman.db"
#   logging.debug('{:%Y-%m-%d %H:%M:%S} Create connection to db'.format(datetime.now()))
#   conn = femmanDb.createConnection(database)

#   logging.debug('{:%Y-%m-%d %H:%M:%S} Fetch all members from db'.format(datetime.now()))
#   members = femmanDb.getAllMembers(conn)

#   logging.debug('{:%Y-%m-%d %H:%M:%S} Create html table output for arr'.format(datetime.now()))
#   rowsToHtml(members)
#   logging.debug('{:%Y-%m-%d %H:%M:%S} Create html table output for admin'.format(datetime.now()))
#   rowsToHtmlAdmin(members)

if __name__ == '__main__':
    main()
