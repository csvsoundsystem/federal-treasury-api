import getpass, imaplib

M = imaplib.IMAP4(os.environ['IMAP_SERVER'])
M.login(os.environ['IMAP_USER'], os.environ['IMAP_SERVER'])
M.select()
typ, data = M.search(None, 'ALL')
for num in data[0].split():
    typ, data = M.fetch(num, '(RFC822)')
    print 'Message %s\n%s\n' % (num, data[0][1])
M.close()
M.logout()
