#!/usr/bin/python3
# -*- coding: utf-8 -*-
import datetime
import logging
import sqlite3
from sqlite3 import Error


# This module contains methods for dealing with the membership (sqlite3) datebase
# mostly stolen from http://www.sqlitetutorial.net/sqlite-python/

def createConnection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    logging.debug("createConnection(db_file)")
    logging.debug("trying to create connection to db")
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)
        logging.debug(e)

    return None

def createTable(conn, createTable_sql):
    """ create a table from the createTable_sql statement
    :param conn: Connection object
    :param createTable_sql: a CREATE TABLE statement
    :return:
    """
    logging.debug("createTable(conn, createTable_sql)")
    try:
        c = conn.cursor()
        c.execute(createTable_sql)
    except Error as e:
        print(e)
        logging.debug(e)

def isMember(conn, member):
    """ check if a member is a member. which means if members email
        already in db, assume member is already a member.
    Query members by email.
    :param conn: the Connection object
    :param member: list of attributes
    :return: bool
    """
    logging.debug("isMember(conn,member)")
    email = member[2].lower()
    logging.debug(email)
    cur = conn.cursor()

    #query db for all members where email is member's emall

    now = datetime.datetime.now()
    year = str(now.year)
    sql = "SELECT * FROM members"+year
    sql += " WHERE email='"+email+"'"
#    cur.execute("SELECT * FROM members? WHERE email=?", (year,email,))
    cur.execute(sql)


    # get the result as rows
    rows = cur.fetchall()

    logging.debug(rows)

    # if email in db check all such entries in db and compare names
#   print(rows)
#   print(member)
    if len(rows) > 0:
#        candName  = member[0].lower()
#        candPrefName  = member[1].lower()


        for row in rows:
            if row[3].lower() == email:
#                print("already member")
#           if candName == row[1].lower() or candPrefName == row[2].lower():
                return row
#                return True
        logging.debug("no member with that name found in db assume not member")
        return None
    else:
        #length of rows is equal to 0 => no such member
        logging.debug("no member with that email adr in db")
        return None

def isMemberNextYear(conn, member):
    """ check if a member is a member. which means if members email
        already in db, assume member is already a member.
    Query members by email.
    :param conn: the Connection object
    :param member: list of attributes
    :return: bool
    """
    logging.debug("isMember(conn,member)")
    email = member[2].lower()
    logging.debug(email)
    cur = conn.cursor()

    #query db for all members where email is member's emall

    now = datetime.datetime.now()
    year = str(now.year+1)
    sql = "SELECT * FROM members"+year
    sql += " WHERE email='"+email+"'"
#    cur.execute("SELECT * FROM members? WHERE email=?", (year,email,))
    cur.execute(sql)


    # get the result as rows
    rows = cur.fetchall()

    logging.debug(rows)

    # if email in db check all such entries in db and compare names
#   print(rows)
#   print(member)
    if len(rows) > 0:
#        candName  = member[0].lower()
#        candPrefName  = member[1].lower()


        for row in rows:
            if row[3].lower() == email:
#                print("already member")
#           if candName == row[1].lower() or candPrefName == row[2].lower():
                return row
#                return True
        logging.debug("no member with that name found in db assume not member")
        return None
    else:
        #length of rows is equal to 0 => no such member
        logging.debug("no member with that email adr in db")
        return None


def insertMember(conn, member):
    """ insert a new member into db
    :param conn:
    :param member:
    :return: member id
    """

    now = datetime.datetime.now()

    sql = '''INSERT INTO members'''+str(now.year)
    sql += '''(fullName,prefName,email,memberDate)
              VALUES(?,?,?,?)'''

    sql = '''INSERT INTO members%s(fullName,prefName,email,memberDate)
              VALUES(?,?,?,?)''' % now.year

    logging.debug("insertMember(conn, member)")
    logging.debug(sql)
    cur = conn.cursor()
    cur.execute(sql, member)
    logging.debug(cur.lastrowid)
    return cur.lastrowid

def insertMemberNextYear(conn, member):
    """ insert a new member into db
        table = currentYear + 1
    :param conn:
    :param member:
    :return: member id
    """

    now = datetime.datetime.now()
    nextYear = now.year+1

    sql = '''INSERT INTO members%s(fullName,prefName,email,memberDate)
              VALUES(?,?,?,?)''' % str(nextYear)

    logging.debug("insertMember(conn, member)")
    logging.debug(sql)
    cur = conn.cursor()
    cur.execute(sql, member)
    logging.debug(cur.lastrowid)
    return cur.lastrowid


def insertMember2(conn, idNr, member):
    """ insert a new member into db
        NOTE! This function is almost identical to the one above but
        differs in the respect that it takes idNr as an argument. this
        function is only meant for usage in "manual" insertion of
        members, when a member already has a membership nr.
    :param conn:
    :param member:
    :param idNr:
    :return: member id
    """
    logging.debug("insertMember2(conn, member)")
    member = tuple([idNr]+list(member))

#    sql = '''INSERT INTO members(id,fullName,prefName,email,memberDate)
#              VALUES(?,?,?,?,?)'''


    now = datetime.datetime.now()
    sql = '''INSERT INTO members'''+str(now.year)
    sql += '''(id,fullName,prefName,email,memberDate)
              VALUES(?,?,?,?,?)'''


    logging.debug(sql)
    cur = conn.cursor()
    cur.execute(sql, member)
    logging.debug(cur.lastrowid)
    return cur.lastrowid

def getAllMembers(conn):
    """ returns all rows in table members from db as a list of rows
    :param conn:
    :return: rows
    """
    logging.debug("getAllMembers(conn)")
    cur = conn.cursor()
    now = datetime.datetime.now()
#    cur.execute("SELECT * FROM members ORDER BY LOWER(prefName);")
    sql = "SELECT * FROM members"+str(now.year)
    sql += " ORDER BY LOWER(prefName);"
    cur.execute(sql)

    rows = cur.fetchall()
    numb = str(len(rows))
    logging.debug("found " +numb)
    print(str(numb)+" members in db")
    return rows

