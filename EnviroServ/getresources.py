# Daily Reports Script
# Renovate Software LTD 2021

import time
import datetime
import os
import sqlite3
from sqlite3 import Error
import psutil


def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except Error as e:
        print(e)

    return conn


def create_record(conn, savedata):
    """
    Create a new record
    :param conn:
    :param ResourceLog:
    :return:
    """
    sql = ''' INSERT INTO MainFrame_resourcelog(datetime,cpu,memory,storage)
              VALUES(?,?,?,?) '''
    cur = conn.cursor()
    cur.execute(sql, savedata)
    conn.commit()
    return cur.lastrowid

def main():
    database = r"db.sqlite3"
    # create a database connection
    conn = create_connection(database)
    with conn:
        try:
            # create a new record
            dateandtime = datetime.datetime.now()
            process = psutil.Process(os.getpid())
            mem = process.memory_info()[0] / float(2 ** 20)  
            cpupercentage = psutil.cpu_percent()
            memoryusage = psutil.virtual_memory()
            memorypercentage = round(mem, 2)
            diskusage = psutil.disk_usage('/')
            diskpercent = format(psutil.disk_usage('/').percent)
            networkusage = psutil.net_io_counters()
            savedata = (dateandtime, cpupercentage, memorypercentage,diskpercent)
            create_record(conn, savedata)
            print("Saved the data correctly.")
            print("System is configured to run every 10 minutes.")
            time.sleep(600)
            main()
            
        except Error as e:
            print(e)

main()