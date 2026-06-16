import random
from django.utils import timezone
from datetime import timedelta


OTP_SESSION_KEY = "voter_otp_code"
OTP_PHONE_SESSION_KEY = "voter_otp_phone"
OTP_VID_SESSION_KEY = "voter_otp_vid"
OTP_ELECTION_SESSION_KEY = "voter_otp_election"
OTP_PURPOSE_SESSION_KEY = "voter_otp_purpose"
OTP_EXPIRES_SESSION_KEY = "voter_otp_expires_at"


def generate_otp():
    return str(random.randint(100000, 999999))


def send_sms_otp(request, *, phone, vid, election_uuid, purpose):
    otp = generate_otp()
    expires_at = timezone.now() + timedelta(minutes=5)

    request.session[OTP_SESSION_KEY] = otp
    request.session[OTP_PHONE_SESSION_KEY] = phone
    request.session[OTP_VID_SESSION_KEY] = vid
    request.session[OTP_ELECTION_SESSION_KEY] = str(election_uuid)
    request.session[OTP_PURPOSE_SESSION_KEY] = purpose
    request.session[OTP_EXPIRES_SESSION_KEY] = expires_at.isoformat()

    return otp


def get_otp_session(request):
    return {
        "otp": request.session.get(OTP_SESSION_KEY),
        "phone": request.session.get(OTP_PHONE_SESSION_KEY),
        "vid": request.session.get(OTP_VID_SESSION_KEY),
        "election_uuid": request.session.get(OTP_ELECTION_SESSION_KEY),
        "purpose": request.session.get(OTP_PURPOSE_SESSION_KEY),
        "expires_at": request.session.get(OTP_EXPIRES_SESSION_KEY),
    }


def is_otp_expired(expires_at_str):
    if not expires_at_str:
        return True

    try:
        expires_at = timezone.datetime.fromisoformat(expires_at_str)
        if timezone.is_naive(expires_at):
            expires_at = timezone.make_aware(expires_at, timezone.get_current_timezone())
    except Exception:
        return True

    return timezone.now() > expires_at


def clear_otp_session(request):
    keys = [
        OTP_SESSION_KEY,
        OTP_PHONE_SESSION_KEY,
        OTP_VID_SESSION_KEY,
        OTP_ELECTION_SESSION_KEY,
        OTP_PURPOSE_SESSION_KEY,
        OTP_EXPIRES_SESSION_KEY,
    ]
    for key in keys:
        request.session.pop(key, None)