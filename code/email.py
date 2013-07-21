import os

import imaplib

import smtplib
from email.mime.text import MIMEText

import logging
import logging.handlers

def login():
    M = imaplib.IMAP4_SSL(os.environ['IMAP_SERVER'])
    M.login(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
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

def send(subject, body):
    'Send an email'
    # http://docs.python.org/2/library/email-examples.html

    msg = MIMEText(body)

    msg['Subject'] = 'The contents of %s' % textfile
    msg['From'] = os.environ['IMAP_USER']
    msg['To'] = 'csv@treasury.io'

    s = smtplib.SMTP(os.envirov['IMAP_SERVER'])
    s.sendmail(msg['From'], [msg['To']], msg.as_string())
    s.quit()

def logger(subject):
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
        mailhost = (os.environ['IMAP_SERVER'], 25),
        fromaddr = os.environ['IMAP_USER'],
        toaddrs = 'csv@treasury.io',
        subject = subject
    )

    logger = logging.getLogger()
    logger.addHandler(smtp_handler)
    return logger
