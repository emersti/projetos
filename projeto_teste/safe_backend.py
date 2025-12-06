from django.core.mail.backends.base import BaseEmailBackend
from boto3 import client
from botocore.exceptions import ClientError
import os
from django.conf import settings


class SESEmailBackend(BaseEmailBackend):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ses = client('ses', region_name=os.getenv("AWS_SES_REGION_NAME", getattr(settings, "AWS_SES_REGION_NAME", "us-west-2")))

    def send_messages(self, email_messages):
        sent = 0
        for message in email_messages:
            try:
                self.ses.send_email(
                    Source=message.from_email,
                    Destination={'ToAddresses': message.to},
                    Message={
                        'Subject': {'Data': message.subject},
                        'Body': {
                            'Text': {'Data': message.body}
                        }
                    }
                )
                sent += 1
            except ClientError as e:
                if not self.fail_silently:
                    raise
        return sent