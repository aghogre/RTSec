# -*- coding: utf-8 -*-
"""
Created on Thu Jan 18 16:18:05 2018

@author: RAVITHEJA
"""

import time
import logging
import pytz
import pymssql
import psycopg2
from config import argument_config
from datetime import datetime, timedelta
from smtpMail import SMTPMail
from apscheduler.schedulers.blocking import BlockingScheduler
from queries import sql_db_queries


def insertIntoPSQL(psqlcon, mssqlcursor):
    """Fetches the given table data from the configured MS SQL server and
    the provided dates for the select query."""

    today_date = datetime.utcnow().date()
    for db_query in sql_db_queries:
        fetch_dates = []
        for n in db_query["reduceDateByDays"]:
            fetch_dates.append(str(today_date - timedelta(days=n)))

        query_template = db_query["query_template"]

        if len(fetch_dates) == 1:
            query = query_template.format(fetch_date=fetch_dates[0])
        elif len(fetch_dates) == 2:
            query = query_template.format(fetch_date1=fetch_dates[0],
                                          fetch_date2=fetch_dates[1])
        logging.info(query)
        mssqlcursor.execute(query)

        columnNames = [desc[0].encode('utf-8')
                       for desc in mssqlcursor.description]
        mssqldata = mssqlcursor.fetchall()

        logging.info("fetched rows: " + str(len(mssqldata)))

        """Inserts the collection data into the given table of configured
        PostgreSQL server."""

        psqltable = db_query["postgresTable"]
        inserted = False
        try:
            psqlcur = psqlcon.cursor()
            row = None
            for d in mssqldata:
                hlist = []
                for t in d:
                    if isinstance(t, unicode):
                        hlist.append(t.encode('utf-8'))
                    else:
                        hlist.append(t)
                row = str(tuple(hlist))
                psqlcur.execute("insert into " + psqltable +
                                " (" + ",".join(columnNames) + ") " +
                                "values " + row)
            psqlcon.commit()
            logging.info(str(len(mssqldata)) + " rows inserted in " +
                         psqltable)
            inserted = True
        except:
            raise

        # Checks whether latest data is inserted into PostgreSQL.
        # Else, sends a failure email notification.
        if not inserted:
            smtp = SMTPMail()
            smtp.sendNotificationMail()


def do_job():
    """Fetches MS SQL server server to fetch data and upload it into
    PostgreSQL server."""

    t1 = time.time()

    # Fetching URLs from Config file.
    mssqlserver = argument_config.get('mssqlserver')
    mssqluser = argument_config.get('mssqluser')
    mssqlpassword = argument_config.get('mssqlpassword')
    mssqldb = argument_config.get('mssqldb')

    psqlserver = argument_config.get('psqlserver')
    psqluser = argument_config.get('psqluser')
    psqlpassword = argument_config.get('psqlpassword')
    psqldb = argument_config.get('psqldb')

    mssqlconn = None
    psqlcon = None
    try:
        # Establishing MS SQL server connection
        mssqlconn = pymssql.connect(mssqlserver, mssqluser, mssqlpassword,
                                    mssqldb)
        mssqlcursor = mssqlconn.cursor()

        # Establishing PostgreSQL server connection
        psqlcon = psycopg2.connect("host=" + psqlserver + " dbname=" + psqldb +
                                   " user=" + psqluser +
                                   " password=" + psqlpassword)

        # Fetches from MS SQL server and inserts into PostgreSQL server.
        insertIntoPSQL(psqlcon, mssqlcursor)
    except:
        raise
    finally:
        if mssqlconn:
            mssqlconn.close()
        if psqlcon:
            psqlcon.close()

    logging.info("Time taken to execute this iteration: " +
                 str(round(float((time.time() - t1)/60), 1)) + " minutes")


def main():
    """Main method"""

    logging.basicConfig(format='%(asctime)s %(levelname)s \
                        %(module)s.%(funcName)s :: %(message)s',
                        level=logging.INFO)

    daily_cron_time_utc = argument_config.get('daily_cron_time_utc').split(':')
    hours, minutes = daily_cron_time_utc[0], daily_cron_time_utc[1]

    # Preparing Scheduler for do_job() with default timezone as UTC.
    scheduler = BlockingScheduler(timezone=pytz.utc)
    scheduler.add_job(do_job, 'cron', hour=hours, minute=minutes)
    scheduler.start()


if __name__ == '__main__':
    main()
