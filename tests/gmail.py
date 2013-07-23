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
      
      email_from = c['account'] + "@gmail.com"
      email_to = c['account'] + "+treasuryiotests@gmail.com"

      headers = "\r\n".join(["from: " + email_from,
                             "subject: " + 'hello from treasury.io (tests)',
                             "to: " + email_to,
                             "mime-version: 1.0",
                             "content-type: text/html"])
      content = headers + "\r\n\r\n" + test_func()
      # body_of_email can be plaintext or html!
      session.sendmail(email_from, email_to, content)
      
    return send_gmail()