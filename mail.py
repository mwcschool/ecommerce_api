from flask import render_template
import os
import requests

KEY = os.getenv('MAILGUN_API_KEY')
SANDBOX = os.getenv('MAILGUN_DOMAIN')


def send_email(sender, receiver, subject, template='default', **kwargs):
    request_url = 'https://api.mailgun.net/v2/{0}/messages'.format(SANDBOX)

    requests.post(
        request_url,
        auth=('api', KEY),
        data={
            'from': sender,
            'to': receiver,
            'subject': subject,
            'html': render_template('mails/{}.html'.format(template), **kwargs)
        }
    )
