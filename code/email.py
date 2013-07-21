import os, imaplib

def login():
    M = imaplib.IMAP4_SSL(os.environ['IMAP_SERVER'])
    M.login(os.environ['IMAP_USER'], os.environ['IMAP_PASSWORD'])
    return M

def main():
    M = login()
    M.select()
    typ, data = M.search(None, '(UNSEEN FROM "fms.treas.gov")')
    for num in data[0].split():
        typ, data = M.fetch(num, '(RFC822)')
        print 'Message %s\n%s\n' % (num, data[0][1])
    M.close()
    M.logout()

main()
