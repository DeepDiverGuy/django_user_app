'''
user_app.twilio_verify
'''

import os

from django.conf import settings

from twilio.rest import Client

from dotenv import load_dotenv




# from dotenv import dotenv_values
# config_var = dotenv_values('.env')
load_dotenv()  # take environment variables from .env.

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
client = Client(account_sid, auth_token)

TWILIO_SERVICE_SID = os.environ['TWILIO_SERVICE_SID']


def token_send(phone):
    
    try:
        verification = client.verify \
                     .v2 \
                     .services(TWILIO_SERVICE_SID) \
                     .verifications \
                     .create(to=str(phone), channel='sms')
        status = verification.status
    except:
        status = 'got error'
    
    return status # verification.status == 'pending', if successful


def token_verify(phone, code):

    try:
        verification_check = client.verify \
                           .v2 \
                           .services(TWILIO_SERVICE_SID) \
                           .verification_checks \
                           .create(to=str(phone), code=str(code))
        status = verification_check.status
    except:
        status = 'got error'

    return status # verification_check.status == 'approved', if successful


