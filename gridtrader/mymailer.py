import logging

logging.basicConfig(level=logging.DEBUG)

def _send_email(user, password, recipient, subject, body):
    import smtplib

    gmail_user = user
    gmail_pwd = password
    FROM = user
    TO = recipient if type(recipient) is list else [recipient]
    SUBJECT = subject
    TEXT = body

    # Prepare actual message
    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(gmail_user, gmail_pwd)
        server.sendmail(FROM, TO, message)
        server.close()
        logging.debug('successfully sent the mail')
    except Exception as e:
        logging.debug('failed to send mail %s', e)


def send_email(account, body):
    _send_email(
        'terrence.brannon@gmail.com',
        'serca972Yancey!',
        'terrence.brannon@gmail.com',
        '({}) ADSactly Grid Trader Error'.format(account),
        body
    )
