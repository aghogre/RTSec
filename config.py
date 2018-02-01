# -*- coding: utf-8 -*-
"""
Created on Thu Oct 12 12:25:49 2017

@author: RAVITHEJA
"""

import os


argument_config = {
    'daily_cron_time_utc': os.getenv('DAILY_CRON_TIME_UTC', ''),

    'mssqlserver': os.getenv('MS_SQL_SERVER', ''),
    'mssqluser': os.getenv('MS_SQL_USER', ''),
    'mssqlpassword': os.getenv('MS_SQL_PASSWORD', ''),
    'mssqldb': os.getenv('MS_SQL_DATABASENAME', ''),

    'psqlserver': os.getenv('POSTGRE_SERVER', ''),
    'psqluser': os.getenv('POSTGRE_USER', ''),
    'psqlpassword': os.getenv('POSTGRE_PWD', ''),
    'psqldb': os.getenv('POSTGRE_DATABASE', ''),

    'from_mail': os.getenv('SENDER_MAILID', ''),
    'to_mail': os.getenv('RECIPIENT_MAILID', ''),
    'mail_pwd': os.getenv('SENDER_PASSWORD', ''),

    'smtp_host': os.getenv('SMTP_HOST_PORT', ''),
    'is_ssl': os.getenv('IS_SSL', False),
    'start_tls': os.getenv('START_TLS', True),

}
