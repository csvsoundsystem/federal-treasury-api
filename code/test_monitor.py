import monitor

def test_login():
    'I should be able to log in.'
    monitor.login()

def test_new_mail():
    _unseen ='(UNSEEN FROM "occurrence@thomaslevine.com" SUBJECT "Test email number 1")'
    _all ='(FROM "occurrence@thomaslevine.com" SUBJECT "Test email number 1")'

    M = monitor.login()
    M.select()

    # Let's make sure that the fixtures are working;
    # we should only have one email called "Test email number 1".
    assert M.search(None, _all)[1] == ['2']

    M.store('2', '-FLAGS', '(\Seen)')

    # The email should be new now.
    assert monitor.new_mail(search_string = _unseen)

    # The email should not be new; we just saw it.
    assert not monitor.new_mail(search_string = _unseen)

    M.close()
    M.logout()

    # Let's check that the email has been seen, just to be sure.
    M = monitor.login()
    M.select()
    assert M.search(None, _unseen)[1] == ['']
    M.close()
    M.logout()
