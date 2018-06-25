import sqlite3
from pathlib import Path
from sqlite3 import Error
import json

class DBconn:
    path = ''

    def connectDB():
        print('connectDB')
        try:
            conn = sqlite3.connect('./tokens.db.sqlite3')
            req = "CREATE TABLE IF NOT EXISTS office " \
                  "( id integer PRIMARY KEY AUTOINCREMENT," \
                  " user text NOT NULL,  " \
                  "mail text NOT NULL,  " \
                  "token text NOT NULL,  " \
                  "access_token text NOT NULL, " \
                  "refresh_token text NOT NULL, " \
                  "expiration integer, " \
                  "session_state text NOT NULL, UNIQUE(mail));"
            conn.execute(req)
            req = "CREATE TABLE IF NOT EXISTS office_mails " \
                  "( id integer PRIMARY KEY AUTOINCREMENT, " \
                  "user_id integer NOT NULL, header text NOT NULL,  " \
                  "body text NOT NULL, time_when text NOT NULL);"
            conn.execute(req)
            req = "CREATE TABLE IF NOT EXISTS office_settings " \
                  "( id integer PRIMARY KEY AUTOINCREMENT, " \
                  "user_id integer NOT NULL, " \
                  "settings text NOT NULL);"
            conn.execute(req)
            conn.commit()
            # write data
            req = "INSERT OR IGNORE INTO office(" \
                  "user, mail, token, " \
                  "access_token, refresh_token, " \
                  "expiration, session_state) VALUES(" \
                  "'test user', 'test@test.org', 'test token', " \
                  "'test access_token', 'test refresh_token'," \
                  "100, 'session state');"
            conn.execute(req)
            req = "INSERT OR IGNORE INTO office_mails(" \
                  "user_id,header,body,time_when) " \
                  "VALUES(1, 'header1', 'body1','10-12-1999');"
            conn.execute(req)
            req = "INSERT OR IGNORE INTO office_mails(" \
                  "user_id,header,body,time_when) VALUES(" \
                  "1, 'header2', 'body2','10-12-1997');"
            conn.execute(req)
            req = "INSERT OR IGNORE INTO office_settings(user_id,settings) VALUES(1, 'settings for account');"
            conn.execute(req)
            conn.commit()
        except Error as e:
            print(e)
        finally:
            conn.close()

    #def getOfficeData(id, ):

    def getAccountsOffice():
        try:
            conn = sqlite3.connect('./tokens.db.sqlite3')
            c = conn.cursor()
            # write data

            req = "select * from office;"
            c.execute(req)
            return c.fetchall()
        except Error as e:
            print(e)
        finally:
            conn.close()

    def getEmailOffice(id):
        try:
            conn = sqlite3.connect('./tokens.db.sqlite3')
            c = conn.cursor()
            # write data

            req = "select * from office_mails where user_id={};".format(id)
            c.execute(req)
            return c.fetchall()
        except Error as e:
            print(e)
        finally:
            conn.close()

    def getRecordFromOffice(user_id):
        try:
            conn = sqlite3.connect('./tokens.db.sqlite3')
            c = conn.cursor()
            # write data
            req = "select * from office where id={};".format(user_id)
            c.execute(req)
            return c.fetchall()
        except Error as e:
            print(e)
        finally:
            conn.close()

    def addTokenOffice(user, mail, token, access_token, refresh_token, expiration, session_state):
        try:
            conn = sqlite3.connect('./tokens.db.sqlite3')
            req = "INSERT INTO office(user, mail, token, access_token," \
                  "refresh_token, expiration, session_state) VALUES(" \
                  "'{}', '{}', '{}','{}','{}',{},'{}');".format(user, mail, json.dumps(token), access_token, refresh_token,
                                                                expiration, session_state)
            conn.execute(req)
            conn.commit()
            return
        except Error as e:
            print(e)
        finally:
            conn.close()


    def refreshTokenOffice(user_id, access_token, refresh_token, expiration):
        try:
            conn = sqlite3.connect('./tokens.db.sqlite3')
            req = "UPDATE office SET (access_token, refresh_token, expiration) = (" \
                  "'{}', '{}', {}) WHERE id = '{}';".fomat(access_token,
                refresh_token, expiration, user_id)
            conn.execute(req)
            conn.commit()
            return
        except Error as e:
            print(e)
        finally:
            conn.close()