import email

def test_login():
    'I should be able to log in.'
    email.login()

def test_new_mail():
    _unseen ='(UNSEEN FROM "occurrence@thomaslevine.com" SUBJECT "Test email number 1")'
    _all ='(FROM "occurrence@thomaslevine.com" SUBJECT "Test email number 1")'

    M = email.login()
    M.select()

    M.store('2', '-FLAGS', '(\Seen)')
    assert email.new_mail(search_string = _unseen)

