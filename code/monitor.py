import os

import imaplib

import smtplib
from email.mime.text import MIMEText

import logging
import logging.handlers

def login():
    M = imaplib.IMAP4_SSL(os.environ['EMAIL_SERVER'])
    M.login(os.environ['EMAIL_USER'], os.environ['EMAIL_PASSWORD'])
    return M

def new_mail(search_string = '(UNSEEN FROM "fms.treas.gov")'):
    'Return True or False.'
    M = login()
    M.select()

    # List the emails
    status, numbers = M.search(None, search_string)

    # Check for new mail
    _new_mail = numbers != ['']

    # Mark new mail as read.
    if _new_mail:
        for number in numbers[0].split():
            M.fetch(number, '(RFC822)')

    # Log out
    M.close()
    M.logout()

    # Return True or False
    return _new_mail

def logger(subject, to = 'csv@treasury.io'):
    '''
    Return a logger that can send errors to email.
    Use it like so.

        l = email.logger('Twitter bot error')
        try:
            break
        except Exception as e:
            l.error(e)

    From http://stackoverflow.com/questions/6182693/python-send-email-when-exception-is-raised
    '''
    smtp_handler = logging.handlers.SMTPHandler(
        mailhost = (os.environ['EMAIL_SERVER'], 587),
        fromaddr = os.environ['EMAIL_USER'],
        toaddrs = to,
        subject = subject,
        credentials = (os.environ['EMAIL_USER'], os.environ['EMAIL_PASSWORD']),
        secure = tuple(),

    )

    logger = logging.getLogger()
    logger.addHandler(smtp_handler)
    return logger
