#!/usr/bin/env python3

import psycopg2
import apikey

 mydb = psycopg2.connect(
     host="localhost",
     database="crypto",
     user="blood",
     password=apikey.dpass)

mycursor = mydb.cursor()

def hisins(uname, data):
  sql = f"INSERT INTO history VALUES(%s, %s)"
  val = (uname, data)
  mycursor.execute(sql, val)
  mydb.commit()

def hisret(uname):
  sql = "SELECT history_data from history where uname=(%s)"
  val = (uname,)
  mycursor.execute(sql, val)
  lis = mycursor.fetchall()
  his = list()
  for i in range(len(lis)):
    no = f"{i+1}. {lis[i][0]}"
    his.append(no)
  return ("\n").join(his)

def hisdel(uname):
  sql = "DELETE from history where uname=(%s)"
  val = (uname,)
  mycursor.execute(sql, val)
  mydb.commit()

def toins(cid, uname, totp):
  sql = f"INSERT INTO otp (chatid, uname, totp) VALUES(%s,%s,%s)"
  val = (cid, uname, totp)
  mycursor.execute(sql, val)
  mydb.commit()

def deldet(cid, table):
  sql = f"DELETE FROM {table} WHERE chatid=(%s)"
  val = (cid,)
  mycursor.execute(sql, val)
  mydb.commit()

def udetails(cid):
    sql = "SELECT * FROM cuser WHERE chatid=(%s)"
    val = (cid,)
    mycursor.execute(sql, val)
    tup = mycursor.fetchall()
    for i in tup:
      return i
  

def checkdet(data, field):
  uval = (data,)
  sql = f"select * from cuser where {field}=%s"
  mycursor.execute(sql, uval) 
  data = mycursor.fetchall()
  if(len(data) == 0):
    return 0
  return 1
  
def retdata():
  sql = "SELECT * FROM cuser"
  mycursor.execute(sql)
  tup = mycursor.fetchall()
  return tup

def inscid(data, field, table):
  sql = f"INSERT INTO {table} ({field}) VALUES (%s)"
  val = (data,)
  mycursor.execute(sql, val)
  mydb.commit()

def insdata(cid, cname, data, table):
  sql = f"UPDATE {table} SET {cname}=(%s) where chatid=(%s);"
  val = (data, cid)
  mycursor.execute(sql, val)
  mydb.commit()


def lcheck(cid):
  sql = f"SELECT uname FROM login WHERE chatid=(%s)"
  val = (cid,)
  mycursor.execute(sql, val)
  lis = mycursor.fetchall()
  if(len(lis) == 1):
    return lis[0]
  return 0

def lpcheck(req, data, field, table):
  sql = f"SELECT {req} FROM {table} WHERE {field}=(%s)"
  val = (data,)
  mycursor.execute(sql, val)
  lis = mycursor.fetchall()
  if(len(lis) == 1):
    return lis[0]
  return 0

def logchat(data):
  sql = "SELECT chatid FROM login where uname=(%s)"
  val = (data,)
  mycursor.execute(sql, val)
  lis = mycursor.fetchall()
  print(lis)
  return lis


if __name__ == "__main__":
  # print(lpcheck("chatid", "Arul", "uname", "login"))
  te = hisret("Arul")
  print(te)
  mydb.commit()


# def insertdb(user):
#   sql = "INSERT INTO cuser (chatid, uname, password, fav) VALUES (%s, %s, %s, %s)"
#   val = (user[0], user[1], user[2], user[3])
#   mycursor.execute(sql, val)
#   mydb.commit()
#   return 1

# def upcount(uname):
#   data = lpcheck("lcount", uname, "uname", "cuser")
#   cnt = data[0] + 1
#   sql = f"UPDATE cuser SET lcount=(%s) where uname=(%s);"
#   val = (cnt, uname)
#   mycursor.execute(sql, val)
#   mydb.commit()

# def downcount(uname):
#   data = lpcheck("lcount", uname, "uname", "cuser")
#   cnt = data[0] - 1
#   sql = f"UPDATE cuser SET lcount=(%s) where uname=(%s);"
#   val = (cnt, uname)
#   mycursor.execute(sql, val)
#   mydb.commit()
