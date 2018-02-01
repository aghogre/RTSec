# Data migration

## Thomson Reuters data pipeline

tr-db_migration is meant for migrating Thomson Reuters data from Microsoft SQL Server database to PostgreSQL Server.
tr-db_migration is loosely-coupled and is flexible to be reused to other data migration applications as well.

This application includes:
* Data migration: MSSQL server (source) to PostgreSql (destination).
* Scheduled execution of SQL queries, as of now UTC timezone.
* Failure Notifications through emails for every query execution.
* Module to backfill historical data - Given a range of dates

## Config params
* **`Scheduler`:** Program gets invoked by the scheduler and executes daily on particular time. 
  *	`{daily_cron_time_utc}`: Time based on UTC timezone, when then Scheduler has to start program execution every day. It should be given in 24 hour format, as HH:MM.

* **`Microsoft SQL Server`:** 
  *	`{mssqlserver}`: IP address and port no. of the source MS SQL server, ex: 'xxx.xxx.xxx.xxx:1433' 
  *	`{mssqluser}`,	`{mssqlpassword}`: Server authentication credentials
  *	`{mssqldb}`: Database name in the server, where required source table is available.
  
* **`Postgre SQL Server`:**
  *	`{psqlserver}`: IP address of the destination Postgre SQL server, ex: 'xxx.xxx.xxx.xxx' 
  *	`{psqluser}`,	`{psqlpassword}`: Server authentication credentials
  *	`{psqldb}`: Database name in the server, where table has to be created.
    
* **`Notification Email ID`:** Happens to notify execution failure through email.
  *	`{from_mail}`: Source email Id
  *	`{to_mail}`: Destination email Id
  *	`{mail_pwd}`: Source email Id's password
 
* **`SMTP Server`:** Configures protocol to send email. 
  *	`{smtp_host}`: SMTP Host along with port number depends on source email account. ex: smtp.gmail.com:587
  *	`{ssl_true}`: SSL depends on the supported SMTP host.
  *	`{start_tls}`: TLS depends on the supported SMTP host.
  
