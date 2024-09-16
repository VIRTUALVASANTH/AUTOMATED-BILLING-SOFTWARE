import os
from sendgrid import SendGridAPIClient
from django.core.mail.backends.base import BaseEmailBackend

class SendGridBackend(BaseEmailBackend):
    def __init__(self, fail_silently=False, **kwargs):
        self.fail_silently = fail_silently
        self.api_client = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))

    def send_messages(self, email_messages):
        for message in email_messages:
            self.api_client.mail.send.post(request_body=message)
        return len(email_messages)