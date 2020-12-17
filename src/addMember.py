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
    memberDate = now
    memberDate = now.strftime("%Y-%m-%d %H:%M:00")
    memberDate = datetime.strptime(memberDate, "%Y-%m-%d %H:%M:00")

    member = [name,name,email,memberDate]
    print(member)

    database = "femman.db"

    # create a database connection
    logging.debug('{:%Y-%m-%d %H:%M:%S} Create connection to db'.format(datetime.now()))
    conn = femmanDb.createConnection(database)
    conn.text_factory = str

    now = datetime.now()
    sqlCreateMembersTable= """ CREATE TABLE IF NOT EXISTS members%s(
                                        id integer PRIMARY KEY,
                                        fullName text NOT NULL,
                                        prefName text NOT NULL,
                                        email    text NOT NULL,
                                        [MemberDate] timestamp NOT NULL
                                    ); """ %str(now.year)
    sqlCreateMembersTableNextYear= """ CREATE TABLE IF NOT EXISTS members%s(
                                        id integer PRIMARY KEY,
                                        fullName text NOT NULL,
                                        prefName text NOT NULL,
                                        email    text NOT NULL,
                                        [MemberDate] timestamp NOT NULL
                                    ); """ %str(now.year+1)

    with conn:

        # create members table table if it doesn't exist, i.e. first
        # time running program

        logging.debug('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())+str(member))

        okCheck = False

        now = datetime.now()
        if now.month >= 11:
            femmanDb.createTable(conn,sqlCreateMembersTableNextYear)
            if not femmanDb.isMemberNextYear(conn, member):
                print("    Adding member to next year's db...")
                memberNumber = femmanDb.insertMemberNextYear(conn, tuple(member))
                print(" "*8 + "Nr: "+ str(memberNumber)+" ("+str(member[3])+")")
                print(" "*8 + member[0].decode('utf-8'))
                print(" "*8 + member[1].decode('utf-8'))
                print(" "*8 +str(member[2])) # email need not be decoded
                if memberNumber:
                    okCheck = True

                moosendResult2 = femmanEmail.moosend(member,"nextYear")
                if moosendResult2 != 0:
                    print("See error above. Add manually. Important!")
                else:
                    print("    ok!")
            else:
                print("Already member in next year's db")


        femmanDb.createTable(conn, sqlCreateMembersTable)
        if not femmanDb.isMember(conn, member): #if not member
            print("    Adding member to database...")
            logging.debug('{:%Y-%m-%d %H:%M:%S} Adding member to db'.format(datetime.now()))
            memberNumber = femmanDb.insertMember(conn, tuple(member))
            print(" "*8 + "Nr: "+ str(memberNumber)+" ("+str(member[3])+")")
            print(" "*8 + member[0].decode('utf-8'))
            print(" "*8 + member[1].decode('utf-8'))
            print(" "*8 +str(member[2])) # email need not be decoded
            logging.debug('{:%Y-%m-%d %H:%M:%S} added to db with nr'.format(datetime.now())+str(memberNumber))

            if memberNumber:
                okCheck = True

            print("        Adding member to moosend")
            moosendResult = femmanEmail.moosend(member,"thisYear")
            if moosendResult != 0:
                print("See error above. Add manually. Important!")
            else:
                print("    ok!")
        else:
            print("already a in member current db")

        if okCheck:
            femmanEmail.sendEmail([memberNumber]+member)

if __name__ == '__main__':
    main()
