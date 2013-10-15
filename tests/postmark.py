import pystmark
import yaml

# gmail helper
def _send_email(tupl):
    subject, message = tupl
    try:
        c = yaml.safe_load(open('../postmark.yml'))
    except:
        print "No email-config file found, just printing the results"
        return
    """
    a decorator to send an email

    """
    msg = pystmark.Message(sender=c['from'], to=c['to'], subject=subject,
                            html=message, tag="tests")
    response = pystmark.send(msg, api_key=c['api_key'])
    try:
      response.raise_for_status()
    except Exception as e:
      print e.message

def email(test_func):
    return _send_email(test_func())