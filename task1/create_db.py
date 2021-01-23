import os
import sqlite3 as sql
import datetime

def init_db():
    with sql.connect('tasks.db') as conn:
        conn.execute('''CREATE TABLE TODO
             (ID INT PRIMARY KEY     NOT NULL,
             TASK TEXT ,
             DUEBY DATE,
             STATUS TEXT);''')
def insert(Id,task,date,status):
    with sql.connect('tasks.db') as conn:
        conn.execute("INSERT INTO TODO (ID,TASK,DUEBY,STATUS) \
                      VALUES (?,?,?,?)",(Id,task,date,status))
def erase():
    with sql.connect('tasks.db') as conn:
        try:
            conn.execute('DROP TABLE TODO')
        except:
            pass

    
erase()
init_db()
insert(1,'first task',datetime.date(2021,1,22),'Not started')
insert(2,'second task',datetime.date(2021,1,22),'Not started')
insert(3,'third task',datetime.date(2021,1,24),'Not started')






