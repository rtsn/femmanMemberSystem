#!/usr/bin/python3
# -*- coding: utf-8 -*-

import femmanEmail
import femmanDb
import logging
from time import sleep
from random import randint
from datetime import *
import os
import sys
from importlib import reload #py3 conv
reload(sys)


def rowsToHtmlAdmin(rows):
    """ this function outputs a html table containing _all_ database
    information and is only meant for admin use.
    :param rows: list of members. one row = one member
    """

    # gen from template

    logging.debug('rowsToHtmlAdmin')
    logging.debug('open templates/htmlHeadTemplateAdmin.txt')
    with open('templates/htmlHeadTemplateAdmin.txt', 'r') as myfile:
        output = myfile.read()

    genDate = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.debug(genDate)

    output = output.replace("[genDate]", genDate)

    for member in rows:
        numb = str(member[0])
#        name = member[1].decode('utf-8')

        name = member[1]
        if not isinstance(name, str):
            name = name.decode('utf-8')
 
        pname = member[2]
        if not isinstance(pname, str):
            pname = pname.decode('utf-8')
        email = member[3]

        d = str(member[4])[:-3] #handle dateTime better

        memberLogStr = numb+" "+name+" "+pname+" "+" "+email+" "+d

        output += """
<tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n</tr>\n""" % (numb,name,pname,email,d)
    output += "</table></body></html>"


    logging.debug("writing output/adminFemmanMemberList.html")
    f = open("output/adminFemmanMemberList.html", "w")
    f.write(str(output))
    f.close()
    logging.debug("closing file")

#for arrare
def rowsToHtml(rows):
    """ this function outputs a html table containing some but not all
    database information on members.
    idnr | prefered name | email | welcome soonest
    welcome soonest in red if not welcome today
    sorted by pref name
    :param rows: list of members. one row = one member
    """

    logging.debug('rowsToHtml')
    logging.debug('open templates/htmlHeadTemplate.txt')

    with open('templates/htmlHeadTemplate.txt', 'r') as myfile:
        output = myfile.read()

    genDate = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    logging.debug(genDate)

    output = output.replace("[genDate]", genDate)

    for member in rows:
        numb = str(member[0])
        name = member[2]
        if not isinstance(name, str):
            name = name.decode('utf-8')
        email = str(member[3])

        memberLogStr = numb+" "+name+" "+name+" "+" "+email
        joinDate = member[4]
        datetime_object = datetime.strptime(joinDate,'%Y-%m-%d %H:%M:%S')
        datetime_object = datetime_object + timedelta(days=1)
        welcomeDate = datetime_object.date()

        welcomeDateStr = str(welcomeDate)
        if welcomeDate > datetime.now().date():
            welcomeDateStr = '<span style="color:#ff0000;"><b>'+welcomeDateStr+'</b></span>'
#       if member[0] == 182: # banned members
#           numb = '<span style="color:#ff0000;"><b></del>'+numb+"</span></b></del>"
#           name = '<span style="color:#ff0000;"><b></del>'+name+"</span></b></del>"
#           email = '<span style="color:#ff0000;"><b></del>'+email+"</span></b></del>"
#           welcomeDateStr = "<b>SUSPENDED</b>"
#           output += """
#tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n</tr>\n""" % (numb,name,email,welcomeDateStr)
#       else:
#           output += """
#<tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n</tr>\n""" % (numb,name,email,welcomeDateStr)

        output += """<tr>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n<td>%s</td>\n</tr>\n""" % (numb,name,email,welcomeDateStr)

    output += "</table></body></html>"

    logging.debug("writing output/FemmanMemberList.html")
    f = open("output/FemmanMemberList.html", "w")
    f.write(str(output))
    f.close()
    logging.debug("closing file")
