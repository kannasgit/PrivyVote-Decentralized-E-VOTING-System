from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from app.models import Election, EligibleVoter
from app.forms import OTPVerificationForm
from app.encryption import (
    sha256_hash,
    normalize_vid,
    encrypt_text,
)

from app.utils.twilio_verify import check_sms_otp


class RegistrationOTPVerifyView(View):
    template_name = "app/voting/register_otp_verify.html"

    def _get_election(self, uuid):
        return get_object_or_404(Election, uuid=uuid)

    def _find_vid_record(self, election, vid):
        return EligibleVoter.objects.filter(
            election=election,
            voter_id_hash=sha256_hash(normalize_vid(vid)),
            is_active=True,
        ).first()

    def get(self, request, uuid):
        election = self._get_election(uuid)

        phone_number = request.session.get("pending_registration_phone")

        if not phone_number:
            messages.error(request, "Session expired. Please register again.")
            return redirect("voter_registration", uuid=election.uuid)

        form = OTPVerificationForm()
        return render(request, self.template_name, {
            "election": election,
            "form": form,
            "phone_last2": phone_number[-2:],
        })

    def post(self, request, uuid):
        election = self._get_election(uuid)

        form = OTPVerificationForm(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {
                "election": election,
                "form": form,
                "phone_last2": (request.session.get("pending_registration_phone") or "")[-2:],
            })

        entered_otp = form.cleaned_data["otp"]

        # 🔥 Get session data
        full_name = request.session.get("pending_registration_full_name")
        phone_number = request.session.get("pending_registration_phone")
        vid = request.session.get("pending_registration_vid")
        pending_election_uuid = request.session.get("pending_registration_election_uuid")

        if not all([full_name, phone_number, vid, pending_election_uuid]):
            messages.error(request, "Session expired. Please register again.")
            return redirect("voter_registration", uuid=election.uuid)

        if pending_election_uuid != str(election.uuid):
            messages.error(request, "Session mismatch.")
            return redirect("voter_registration", uuid=election.uuid)

        # 🔥 VERIFY OTP USING TWILIO
        if not check_sms_otp(phone_number, entered_otp):
            messages.error(request, "Invalid OTP.")
            return render(request, self.template_name, {
                "election": election,
                "form": OTPVerificationForm(),
                "phone_last2": phone_number[-2:],
            })

        # 🔥 Fetch voter
        voter = self._find_vid_record(election, vid)

        if not voter:
            messages.error(request, "Invalid VID.")
            return redirect("voter_registration", uuid=election.uuid)

        if voter.is_registered:
            messages.error(request, "This VID is already registered.")
            return redirect("voter_registration", uuid=election.uuid)

        # 🔥 Save registration
        voter.full_name = full_name
        voter.phone_encrypted = encrypt_text(phone_number)
        voter.phone_last2 = phone_number[-2:]
        voter.is_registered = True
        voter.registered_at = timezone.now()
        voter.save(update_fields=[
            "full_name",
            "phone_encrypted",
            "phone_last2",
            "is_registered",
            "registered_at",
        ])

        # 🔥 Clear session
        request.session.pop("pending_registration_full_name", None)
        request.session.pop("pending_registration_phone", None)
        request.session.pop("pending_registration_vid", None)
        request.session.pop("pending_registration_election_uuid", None)

        messages.success(request, "Registration completed successfully.")
        return redirect("election_detail", uuid=election.uuid)