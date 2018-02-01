# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 13:25:44 2018

@author: RAVITHEJA
"""

import logging
import smtplib
from config import argument_config


class SMTPMail:
    """Making use of SMTP to send emails."""

    def sendNotificationMail(self):
        """Sends notification mail for any failure in scheduler process."""

        logging.basicConfig(format='%(asctime)s %(levelname)s \
                            %(module)s.%(funcName)s :: %(message)s',
                            level=logging.INFO)

        logging.warn("Sending Email notification... Make sure sender email " +
                     "account allows less secure apps access, especially for" +
                     " gmail - 'https://myaccount.google.com/security'")

        # Fetching user arguments.
        from_mail = argument_config.get('from_mail')
        to_mail = argument_config.get('to_mail')
        mail_pwd = argument_config.get('mail_pwd')
        smtp_host = argument_config.get('smtp_host')
        is_ssl = argument_config.get('is_ssl')
        start_tls = argument_config.get('start_tls')

        subject = "THOMSON REUTERS DB MIGRATION FAILURE NOTIFICATION."
        body_text = "\r\n\r\n THOMSON REUTERS DB MIGRATION FAILED " +\
                    "TO EXECUTE TODAY'S SCHEDULED EXECUTION"

        headers = ["From: " + from_mail,
                   "Subject: " + subject,
                   "To: " + to_mail,
                   "MIME-Version: 1.0",
                   "Content-Type: text/html"]

        headers = "\r\n".join(headers)
        server = None
        try:
            server = smtplib.SMTP(smtp_host)
            # server.set_debuglevel(True)
            if is_ssl:
                pass
            if start_tls:
                server.starttls()

            logging.debug("Authenticating email account.")
            server.login(from_mail, mail_pwd)
            server.sendmail(from_addr=from_mail, to_addrs=to_mail,
                            msg=headers + "\r\n\r\n" + body_text)

            logging.info("Email sent successfully.")
        except:
            logging.error("SMTP exception...")
            raise
        finally:
            server.quit()
