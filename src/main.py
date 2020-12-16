#!/usr/bin/python3
# -*- coding: utf-8 -*-

import femmanEmail
import femmanDb
import femmanMisc
import logging

from datetime import *
from time import sleep
from random import randint

import os
import sys
from importlib import reload #py3 conv
reload(sys)

#This is the main module, containing the main function where all the
#modular components are combined. It also contains functions for
#generating membership html tables

def main():
    logFIleName = 'logs/femmanLog-{:%Y-%m-%d}'.format(datetime.now())
    logging.basicConfig(filename=logFIleName,level=logging.DEBUG)
    logging.debug('')
    logging.debug('{:%Y-%m-%d %H:%M:%S} Starting Script'.format(datetime.now()))
    print("Checking email...")
    logging.debug('{:%Y-%m-%d %H:%M:%S} Checking Email'.format(datetime.now()))
    newMembers = femmanEmail.readEmailFromGmail()

    if newMembers:
        logging.debug('{:%Y-%m-%d %H:%M:%S} Member candidates found'.format(datetime.now()))
        #if there exists new potential members count them
        counter = 0
        database = "femman.db"

        #make a db connection
        logging.debug('{:%Y-%m-%d %H:%M:%S} Create connection to db'.format(datetime.now()))
        conn = femmanDb.createConnection(database)

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
            logging.debug('{:%Y-%m-%d %H:%M:%S} Creating table'.format(datetime.now()))
            femmanDb.createTable(conn, sqlCreateMembersTable)
            memberCandsStr = "\n"+str(len(newMembers))+" candidates"
            print(memberCandsStr)
            logging.debug('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())+memberCandsStr)
            print("\nStart processing...\n")

            logging.debug('{:%Y-%m-%d %H:%M:%S} Start processing members'.format(datetime.now()))
            maxLen = 0
            outputString = ""
            for member in newMembers:
                logging.debug('{:%Y-%m-%d %H:%M:%S}'.format(datetime.now())+str(member))
                #if already a member go to next candidate

                memberInfo = femmanDb.isMember(conn, member)
                if memberInfo: #is member
                    logging.debug('{:%Y-%m-%d %H:%M:%S} Already member'.format(datetime.now()))
                    ouputString = member[0].decode('utf-8')+","
                    ouputString += member[1].decode('utf-8')+","
                    ouputString += member[2]+","
                    ouputString += str(member[3]) + " already a member"
#                    outputString = str(member)+ " already a member"
#                    print(outputString)


                    now = datetime.now()
                    if now.month >= 11:

                        newDate = member[-1]
                        oldDate = memberInfo[4]
                        oldDate = datetime.strptime(oldDate,'%Y-%m-%d %H:%M:%S')

                        tmpStr = str(now.year)+"/12/1"
                        firstDec = datetime.strptime(tmpStr, '%Y/%m/%d')

                        if newDate > oldDate and newDate >= firstDec:

                            #make sure table exists
                            femmanDb.createTable(conn,sqlCreateMembersTableNextYear)
                            logging.debug('{:%Y-%m-%d %H:%M:%S} Adding member to db'.format(datetime.now()))
                            if not femmanDb.isMemberNextYear(conn, member):
                                print("    Adding member to next year's db...")
                                memberNumber = femmanDb.insertMemberNextYear(conn, tuple(member))
                                print(" "*8 + "Nr: "+ str(memberNumber)+" ("+str(member[3])+")")
                                print(" "*8 + member[0].decode('utf-8'))
                                print(" "*8 + member[1].decode('utf-8'))
                                print(" "*8 +str(member[2])) # email need not be decoded

                                moosendResult2 = femmanEmail.moosend(member,"nextYear")
                                if moosendResult2 != 0:
                                    print("See error above. Add manually. Important!")
                                else:
                                    print("    ok!")
                                print("        Emailing welcome msg...")
                                femmanEmail.sendEmail([memberNumber]+member)
                                counter +=1

                    if len(outputString) > maxLen:
                        maxLen = len(outputString)
                    padding= " "*(maxLen - len(outputString) +1)
                    #check if script is run from cron or console
                    if os.isatty(sys.stdin.fileno()):
                        sys.stdout.write("\r" + outputString+padding)
                        sys.stdout.flush()
                    else:
                        pass
                    continue
                else:
                    print()
                    print("New member!")
                    logging.debug('{:%Y-%m-%d %H:%M:%S} New member'.format(datetime.now()))

                counter += 1

                print("    Adding member to database...")
                logging.debug('{:%Y-%m-%d %H:%M:%S} Adding member to db'.format(datetime.now()))
                memberNumber = femmanDb.insertMember(conn, tuple(member))
                print(" "*8 + "Nr: "+ str(memberNumber)+" ("+str(member[3])+")")
                print(" "*8 + member[0].decode('utf-8'))
                print(" "*8 + member[1].decode('utf-8'))
                print(" "*8 +str(member[2])) # email need not be decoded
                logging.debug('{:%Y-%m-%d %H:%M:%S} added to db with nr'.format(datetime.now())+str(memberNumber))

                now = datetime.now()
                if now.month >= 11: # add to next year's db
                    femmanDb.createTable(conn,sqlCreateMembersTableNextYear)
                    if not femmanDb.isMemberNextYear(conn, member):
                        print("    Adding member to next year's db...")
                        memberNumber = femmanDb.insertMemberNextYear(conn, tuple(member))
                        print(" "*8 + "Nr: "+ str(memberNumber)+" ("+str(member[3])+")")
                        print(" "*8 + member[0].decode('utf-8'))
                        print(" "*8 + member[1].decode('utf-8'))
                        print(" "*8 +str(member[2])) # email need not be decoded

                        print("    Adding member to next year's moosend...")
                        moosendResult2 = femmanEmail.moosend(member,"nextYear")
                        if moosendResult2 != 0:
                            print("See error above. Add manually. Important!")
                        else:
                            print("    ok!")
                logging.debug('{:%Y-%m-%d %H:%M:%S} Sleep 2s'.format(datetime.now()))


                print("    Sleep 2s")
#                sleep(2)
                print("        Adding member to moosend")
                moosendResult = femmanEmail.moosend(member,"thisYear")
                moosendResult2 = femmanEmail.moosend(member,"nextYear")
                if moosendResult != 0 or moosendResult2 != 0:
                    print("See error above. Add manually. Important!")
                else:
                    print("    ok!")
                print("        Emailing welcome msg...")

                logging.debug('{:%Y-%m-%d %H:%M:%S} Email welcome msg'.format(datetime.now()))
                femmanEmail.sendEmail([memberNumber]+member)

                #if there is more than one new members and we have more
                #members to process, sleep a little to make google happy
                if len(newMembers) > 1 and newMembers.index(member) < len(newMembers)-1:
                    sleepTime = randint(1,5)
                    sleepStr = "Sleep for "+str(sleepTime)+ "s to not make google angry"
                    print(sleepStr)
                    logging.debug('{:%Y-%m-%d %H:%M:%S} '.format(datetime.now())+sleepStr)
                    sleep(sleepTime)

            CURSOR_UP = '\033[F'
            ERASE_LINE = '\033[K'
            print(CURSOR_UP + ERASE_LINE)
            padding = " "*(maxLen - 25)
            sys.stdout.write("\rdone checking candidates "+padding)
            sys.stdout.flush()
            print()
            if counter > 0:
                addStr = "Added "+str(counter)+" new members to db"
                print(addStr)
                logging.debug('{:%Y-%m-%d %H:%M:%S} '.format(datetime.now())+addStr)
            else:
                addStr = "No new members added to db."
                print(addStr)
                logging.debug('{:%Y-%m-%d %H:%M:%S} '.format(datetime.now())+addStr)
    else:
        elseMsg = "No member candidates found. Probably indicates some error."
        logging.debug('{:%Y-%m-%d %H:%M:%S} '.format(datetime.now())+elseMsg)
        print(elseMsg)

    logging.debug('{:%Y-%m-%d %H:%M:%S} Create HTML outputs'.format(datetime.now()))
    database = "femman.db"
    conn = femmanDb.createConnection(database)
    members = femmanDb.getAllMembers(conn)
    femmanMisc.rowsToHtml(members)
    femmanMisc.rowsToHtmlAdmin(members)

if __name__ == '__main__':
    main()
