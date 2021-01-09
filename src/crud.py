from flask import *
import sqlite3

import femmanEmail
import femmanDb
#import femmanMisc

from datetime import *
import datetime

from time import sleep



app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html");

@app.route("/add")
def add():
    return render_template("add.html")

@app.route("/savedetails",methods = ["POST","GET"])
def saveDetails():
    now = datetime.datetime.now()
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

    database = "femman.db"
    msg = "msg"
    if request.method == "POST":
         try:
            fullName = request.form["fullName"].strip()
            prefName = request.form["prefName"].strip()
            email = request.form["email"].strip()

            if fullName == "" or prefName == "":
                print("no field can be empty")
                subMsg = "no field can be empty"
                raise Exception('No field can be empty')


            fullName = fullName.encode("utf-8")
            prefName = prefName.encode("utf-8")

            memberDate = now
            memberDate = now.strftime("%Y-%m-%d %H:%M:00")
            memberDate = datetime.datetime.strptime(memberDate, "%Y-%m-%d %H:%M:00")
            member = [fullName,prefName,email,memberDate]
            print(member)

            conn = femmanDb.createConnection(database)
            conn.text_factory = str

            subMsg = ""
            with conn:
                okCheck = False

                now = datetime.datetime.now()
                if now.month >= 11:
                    femmanDb.createTable(conn,sqlCreateMembersTableNextYear)
                    if not femmanDb.isMemberNextYear(conn, member):
                        print("    Adding member to next year's db...")
                        memberNumber = femmanDb.insertMemberNextYear(conn, tuple(member))
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
#                    print("    Adding member to database...")
                    memberNumber = femmanDb.insertMember(conn, tuple(member))
                    if memberNumber:
                        okCheck = True
#                    print("        Adding member to moosend")
                    moosendResult = femmanEmail.moosend(member,"thisYear")
                    if moosendResult != 0:
                        print("See error above. Add manually. Important!")
                else:
                    print("already a in member current db")
                    subMsg = "\nalready a member (email already exists in list)"

                if okCheck:
                    femmanEmail.sendEmail([memberNumber]+member)
                    msg = "Member successfully Added "+str(memberNumber)
                else:
                    msg = subMsg
         except Exception as e:
             print("some error")
             msg = str(e)
#             msg = "We can not add the member to the list"+subMsg
         finally:
            return render_template("success.html",msg = msg)
            conn.close()



@app.route("/view")
def view():
    con = sqlite3.connect("femman.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    now = datetime.datetime.now()
    sql = "SELECT * FROM members"+str(now.year)
    sql += " ORDER BY LOWER(prefName);"
    cur.execute(sql)

    dictrows = [dict(row) for row in cur]

    for r in dictrows:
        prefName = r['prefName']
        if not isinstance(r['prefName'], str):
            prefName = prefName.decode("utf-8")
            r['prefName'] = r['prefName'].decode("utf-8")

        joinDate = r['MemberDate']
        datetime_object = datetime.datetime.strptime(joinDate,'%Y-%m-%d %H:%M:%S')
        datetime_object = datetime_object + timedelta(days=1)
        welcomeDate = datetime_object.date()

        welcomeDateStr = str(welcomeDate)
        if welcomeDate > datetime.datetime.now().date():
            welcomeDateStr = '<span style="color:#ff0000;"><b>'+welcomeDateStr+'</b></span>'

        r['MemberDate'] = Markup(welcomeDateStr)

    cur.execute(sql)
    rows = list(cur.fetchall())
#    return render_template("view.html",rows = rows)
    return render_template("view.html",rows = dictrows)

@app.route("/viewFull")
def viewFull():
    con = sqlite3.connect("femman.db")
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    now = datetime.datetime.now()
    sql = "SELECT * FROM members"+str(now.year)
    sql += " ORDER BY LOWER(prefName);"
    cur.execute(sql)

    dictrows = [dict(row) for row in cur]

    for r in dictrows:
        prefName = r['prefName']
        fullName = r['fullName']
        if not isinstance(r['prefName'], str):
            prefName = prefName.decode("utf-8")
            r['prefName'] = r['prefName'].decode("utf-8")

        if not isinstance(r['fullName'], str):
            fullName = fullName.decode("utf-8")
            r['fullName'] = r['fullName'].decode("utf-8")

    cur.execute(sql)
    rows = list(cur.fetchall())
#    return render_template("view.html",rows = rows)
    return render_template("viewFull.html",rows = dictrows)


@app.route("/delete")
def delete():
    return render_template("delete.html")

@app.route("/deleterecord",methods = ["POST"])
def deleterecord():
    id = request.form["id"]
    with sqlite3.connect("femman.db") as con:
        try:
            cur = con.cursor()
            now = datetime.datetime.now()
            sql = "delete from members"+str(now.year)+ " where id = "+str(id)+";"
            cur.execute(sql)
            msg = "record successfully deleted"
        except Exception as e:
            print(e)
            msg = "can't be deleted"
        finally:
            return render_template("delete_record.html",msg = msg)

@app.route("/edit")
def edit():
    return render_template("edit.html")

@app.route("/editrecord",methods = ["POST"])
def editrecord():
    id = request.form["id"]
    msg = str(id)
    return render_template("edit_record.html",msg = msg)


@app.route("/ban")
def ban():
    return render_template("ban.html")

@app.route("/banrecord",methods = ["POST"])
def banrecord():
    now = datetime.datetime.now()
    sqlCreateBannedTable= """ CREATE TABLE IF NOT EXISTS banned%s(
                                        id integer PRIMARY KEY,
                                        fullName text NOT NULL,
                                        prefName text NOT NULL,
                                        email    text NOT NULL,
                                        [MemberDate] timestamp NOT NULL
                                    ); """ %str(now.year)

    database = "femman.db"
    conn = femmanDb.createConnection(database)
    conn.text_factory = str

    subMsg = ""
#    with conn:

    femmanDb.createTable(conn,sqlCreateMembersTableNextYear)
    print("--------------")
    #create bannedYear if not exists
#    if request.method == "POST":
#         try:
#            fullName = request.form["fullName"].strip()

    id = request.form["id"]
    action = request.form["action"]

    print(type(request.form))
    print(request.form)
    print(id)
    print(action)
    print("-----")
    msg = ".."

    # first get info from member id
    # then check if email in banned

    return render_template("ban_record.html",msg = msg)


if __name__ == "__main__":
    app.run(debug = True)
