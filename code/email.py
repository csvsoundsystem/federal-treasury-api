import os, imaplib

def login():
    M = imaplib.IMAP4_SSL(os.environ['IMAP_SERVER'])
    M.login(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
    return M

def previous_email(search_string = '(FROM "fms.treas.gov")'):
    M = login()
    M.select()

    # List the emails
    status, header = M.search(None, search_string)
    num = header[0].split()[-1]

    # Read the most recent one.
    status, eml = M.fetch(num, '(RFC822)')
    print eml[0][1]

    M.close()
    M.logout()
