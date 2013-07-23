import smtplib
import yaml, os

def send_test_result_via_gmail(msg):
    c = yaml.safe_load(open('../gmail.yml').read())
    # The below code never changes, though obviously those variables need values.
    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.ehlo()
    session.starttls()
    session.login(c['account'], c['password'])
    # # This is how you send an email in Python:

    headers = "\r\n".join(["from: " + c['account']+"@gmail.com",
                           "subject: " + 'hello',
                           "to: " + c['account']+"+treasuryiotests@gmail.com",
                           "mime-version: 1.0",
                           "content-type: text/html"])

    # body_of_email can be plaintext or html!
    session.sendmail(c['main_account']+"@gmail.com", 'csvsoundsystem+treasuryiotests@gmail.com', msg)