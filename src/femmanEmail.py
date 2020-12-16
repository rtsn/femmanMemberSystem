#!/usr/bin/python3
# -*- coding: utf-8 -*-

# This modules provides methods for reading and parsing information from
# the below specified gmail account.

import smtplib
import time
import imaplib
import email
import logging
import sys
import os
import configparser

from datetime import datetime
from datetime import timedelta

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header

import requests

config = configparser.ConfigParser()
config.read('auth')

# Constants (remember to enable "unsecure" apps in gmail account
ORG_EMAIL   = "@gmail.com"
FROM_EMAIL  = config['gmail']['user']+ ORG_EMAIL
FROM_PWD    = config['gmail']['pw']
SMTP_SERVER = "imap.gmail.com"
SMTP_PORT   = 993

#moosend
APIKEY = config['moosend']['apiKey']
THISYEAR = config['moosend']['thisYear']
NEXTYEAR = config['moosend']['nextYear']


def parseDate(dateLine):
    """ convert string
        dateLine = "Order #00001. Placed on October 6, 2018 at 3:06 PM GMT+2."
        to datetime object to be added as membership attribute for later
        insertion into db.
    :param dateLine: string
    :return date: datetime object
    """
    logging.debug("parseDate(dateLine)")

    #These two lines could certainly be made more pythonic
    dateLine = dateLine.split("Placed on ")[1]
    dateLine = dateLine[:dateLine.find(' GMT')]
    logging.debug(dateLine)

    date = datetime.strptime(dateLine, '%B %d, %Y at %I:%M %p')
    logging.debug(date)
    return date

def extractInfo(body):
    """ extract info (name, pref name, email, dateString) from
        body = msg.get_payload(decode=True). returns this info as
        list.
    :param body: msg.get_payload(decode=True)
    :return member: list
    """
    cost = 100

    logging.debug("extractinfo(body)")
    #Split the body into a list of lines for easier parsing

    b = body.decode("utf-8")
    body = b
    body = body.replace('\r', '\n')
    bodyLines = body.split('\n')
    bodyLines[:] = [x for x in bodyLines if x]

    ind = bodyLines.index(" SUBTOTAL")+2

    if bodyLines[ind] != "Membership":
        logging.debug("Product check failed")
        return []

    fullName = ""
    preferredName = ""
    emailAdr = ""
    membershipDate = ""
    ind = bodyLines.index(" TOTAL")+2
    totalCost = bodyLines[ind]
    totalCost = totalCost[1:-6].strip()
    totalCost = int(totalCost.replace(",",""))
    numberOfRuns = totalCost/cost

    if totalCost > cost:
        logging.debug("Multiple memberships bought!!"+str(numberOfRuns))

    counter = 0
    members = []
    # product could potentially be something other than 'membership'
    # e.g. t-shirt so productCheck should insure that we are dealing
    # with a new member and not someone trying to buy something.

    productCheck = False

    # go through all the body lines and when the info is found stop and
    # return the list (given that productCheck is equal to true.
    lineCount = 0
    for line in bodyLines:
        i = lineCount
        if "Order" in line and "Placed on" in line:
            logging.debug("'Order' and 'Placed on' found in line")
            membershipDate = parseDate(line)

        elif "Full legal name:" in line or "Full given name:" in line:
            fullName = bodyLines[i+1].strip()
            logging.debug("Full name: "+fullName)
            fullName = fullName.encode('utf-8')

        elif "Preferred name:" in line:
            preferredName = bodyLines[i+1].strip()
            logging.debug("Prefered name: "+preferredName)
            preferredName = preferredName.encode('utf-8')

        elif "Email:" in line:
            emailAdr = bodyLines[i+1].strip()
            logging.debug("email converted to lower case: "+emailAdr)
            emailAdr = emailAdr.lower()
            counter += 1
            member = [fullName,preferredName,emailAdr,membershipDate]
            members.append(member)
            if counter == numberOfRuns:
                break
        lineCount += 1

    if totalCost > cost:
        #if date reasonable
        compareDate = datetime.now() - timedelta(days=1)
        firstDate = members[0][3]
        if firstDate >= compareDate:
            print("\nWarning: totalCost > cost maybe check it out")
            for member in members:
                print(member)
    return members

def readEmailFromGmail():
    """ this method goes through _every_ email in the above specified
        gmail inbox. if a mail passes some checks then we try to extract
        membership attributes from the email body and add it to a list
        of potential member candidates which then is returned.

    :param member: a list of info (name, pref name, email, date
    :return newMemberList:
    """
    logging.debug("readEmailFromGmail")
    newMemberList = []

    logging.debug("trying to connect to gmail")
    try:
        #connect to gmail and select inbox
        mail = imaplib.IMAP4_SSL(SMTP_SERVER)
        mail.login(FROM_EMAIL,FROM_PWD)
        mail.select('inbox')

        type, data = mail.search(None, 'ALL')
        mail_ids = data[0]

        logging.debug("connection seems ok")
        id_list = mail_ids.split() #determine range for for loop
        first_email_id = int(id_list[0])
        latest_email_id = int(id_list[-1])
        logging.debug("first_email_id " +str(first_email_id))
        logging.debug("latest_email_id " +str(latest_email_id))

        #go through every email in inbox
        counter = 0

        for i in range(latest_email_id,first_email_id, -1):
            type, data = mail.fetch(str(i), '(RFC822)' )
#            result, data = mail.fetch(str(message_id), "(RFC822)")
#py3 https://stackoverflow.com/questions/14080629/python-3-imaplib-fetch-typeerror-cant-concat-bytes-to-int
            for response_part in data:
                if isinstance(response_part, tuple):
                    msg = email.message_from_bytes(response_part[1])
                    email_from = msg['from']
                    # First check, if "from" not correct, skip email
                    logging.debug("first check from == Squarespace <no-reply@squarespace.com>")
                    if "Squarespace <no-reply@squarespace.com>" not in email_from:
                        logging.debug("first check failed "+ str(email_from))
                        continue
                    logging.debug("first check ok")
                    logging.debug("second check subject == Kulturhuset Femman: A New Order has Arrived")
                    email_subject = msg['subject']
                    email_subject = email_subject.replace("\r", "\n")
                    email_subject = email_subject.replace("\n", "")
                    checkString = "Kulturhuset Femman: A New Order has Arrived"

                    if checkString not in email_subject:
                        logging.debug("second check failed "+ str(email_subject))
                        continue
                    else:
                        logging.debug("second check ok")
                        body = msg.get_payload(decode=True)
                        body = msg.get_payload()
                        if msg.is_multipart():
                            for part in msg.get_payload():
                                body = part.get_payload()[0]
                                body = body.get_payload(decode=True)
                        if body == None:
                            logging.debug("body = None")
                            continue
                        logging.debug("extract member info from email body")
                        members = extractInfo(body)
                        if members != []: #if if nothing went wrong in extraction
                            logging.debug(str(members))
                            logging.debug("append member(s) to member candidate list")
                            newMemberList += members
                            counter = len(newMemberList)

                            #check if run from cron
                            if os.isatty(sys.stdin.fileno()):
                                sys.stdout.write("\r" + str(counter) + " member candidates found")
                                sys.stdout.flush()
                            else:
                                pass
                        else:
                            print("    Product == Membership check failed!")
                            logging.debug("something failed! members = []")
        logging.debug("return newMemberList")
        print()

        if not os.isatty(sys.stdin.fileno()):
            print(str(len(newMemberList))+ "  member candidates found")

        return newMemberList
    except Exception as e: #print std error
        logging.debug(e)
        print(str(e))

def sendEmail(member):
    """ Sends a welcome email, specified by a template, to a new member
    :param member: a list of info (name, pref name, email, date)
    :return:
    """
    logging.debug('sendEmail')
    logging.debug(str(member))
    sentFrom = FROM_EMAIL

    subject = 'Welcome to Femman!'

    applicationDate = member[4]
    logging.debug("applicationDate: "+str(applicationDate))

    #this snippet calculates when a new member is welcome to kulturhuset
    #at the sonest, i.e. applicationDate+1 day
    datetime_object = applicationDate + timedelta(days=1)
    welcomeDate = datetime_object.date()
    logging.debug("welcomeDate: "+str(welcomeDate))

    # this calcs how long membership is. if payed before or including
    # oct 1 then member ship is applicationYear + nextyear.
    applicationYear = applicationDate.year

    tmpStr = str(applicationYear)+"/12/1"
    firstDec = datetime.strptime(tmpStr, '%Y/%m/%d')
    welcomeYearString = str(applicationYear)
    # depening on application year edit welcomeYearString
    if applicationDate >= firstDec:
        welcomeYearString += " AND "+str(applicationYear+1)

    logging.debug("welcomeYear: "+str(welcomeYearString)) #for hello msg
    prefName = member[2].decode('utf-8')

    with open('templates/welcomeMail.txt', 'r') as myfile:
        body = myfile.read()

    body = body.replace("[preferredName]", prefName) #edit variables by replacing them
    body = body.replace("[welcomeDate]", str(welcomeDate))
    body = body.replace("[yearString]", welcomeYearString)
    body = body.encode("utf-8")

    frm = sentFrom
    msg = MIMEMultipart('alternative')
    msg.set_charset('utf8')
    msg['FROM'] = sentFrom

    to = member[3]

    bodyStr = body
    msg['Subject'] = subject
    msg['To'] = to
    _attach = MIMEText(bodyStr, 'plain', 'UTF-8')
    msg.attach(_attach)

    try:
        logging.debug("trying to send email")
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(FROM_EMAIL, FROM_PWD)
        server.sendmail(frm, to, msg.as_string())
        server.close()

        print('    Email sent to '+member[2].decode('utf-8'))
        print('    '+to)
        logging.debug("Email sent to "+member[2].decode('utf-8'))
    except Exception as e:
        print(e)
        logging.debug(e)

def moosend(member,year):
    logging.debug("Add new member to moosend. moosend(member)")
    name = member[1]
    email = member[2]

    headers = {
        'Content-Type': 'application/json',
    }

    params = (
        ('apikey', APIKEY),
    )

    data = '{"Name":"'+name.decode('utf-8')+'","Email":"'+email+'","HasExternalDoubleOptIn":true}'
    logging.debug(data)

    if year == "thisYear":
        listId = THISYEAR
    elif year == "nextYear":
        listId = NEXTYEAR
    url = 'https://api.moosend.com/v3/subscribers/'+listId+'/subscribe.json'
    response = requests.post(url, headers=headers, params=params, data=data.encode('utf-8'))


    logging.debug(response.json())
    code = response.json()['Code']

    if code != 0:
        print("Error adding member to moosend")
        print(response.json()['Error'])
        logging.debug(response.json()['Error'])
    else:
        logging.debug("all good. member added to moosend")
    return code

