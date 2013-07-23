import smtplib
import yaml, os


# gmail helper
def gmail(test_func):
    """
    a decorator to send an email

    """
    def send_gmail():
      c = yaml.safe_load(open('../gmail.yml').read())
      # The below code never changes, though obviously those variables need values.
      session = smtplib.SMTP('smtp.gmail.com', 587)
      session.ehlo()
      session.starttls()
      session.login(c['account'], c['password'])
      
      headers = "\r\n".join(["from: " + c['account'],
                             "subject: " + c['subject'],
                             "to: " + c['account'],
                             "mime-version: 1.0",
                             "content-type: text/html"])
      content = headers + "\r\n\r\n" + test_func()
      # body_of_email can be plaintext or html!
      session.sendmail(c['account'], c['account'], content)
      
    return send_gmail()