from twilio.rest import Client
from django.conf import settings


def get_twilio_client():
    return Client(
        settings.TWILIO_ACCOUNT_SID,
        settings.TWILIO_AUTH_TOKEN,
    )


def send_sms_otp(phone):
    client = get_twilio_client()
    verification = client.verify.v2.services(
        settings.TWILIO_VERIFY_SERVICE_SID
    ).verifications.create(
        to=f"+91{phone}",
        channel="sms",
    )
    return verification.status


def check_sms_otp(phone, code):
    client = get_twilio_client()
    result = client.verify.v2.services(
        settings.TWILIO_VERIFY_SERVICE_SID
    ).verification_checks.create(
        to=f"+91{phone}",
        code=code,
    )
    return result.status == "approved"