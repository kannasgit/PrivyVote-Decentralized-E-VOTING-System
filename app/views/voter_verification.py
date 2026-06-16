from django.views import View
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone

from app.models import (
    Election,
    EligibleVoter,
    VoterVerification,
    Vote,
    ElectionVoterSession,
)

from app.encryption import (
    sha256_hash,
    normalize_vid,
    normalize_phone,
    generate_otp,
    decrypt_text,
)


class VoterVerificationView(LoginRequiredMixin, View):
    template_name = "app/voting/verify_voter.html"

    def _block_admin(self, request):
        return request.user.is_authenticated and request.user.is_staff

    def _get_election(self, uuid):
        return get_object_or_404(Election, uuid=uuid)

    def _find_voter(self, election, vid):
        return EligibleVoter.objects.filter(
            election=election,
            voter_id_hash=sha256_hash(normalize_vid(vid)),
            is_active=True,
        ).first()

    def _already_voted(self, election, voter_hash):
        return Vote.objects.filter(
            election=election,
            voter_hash=voter_hash,
        ).exists()

    def get(self, request, uuid):
        if self._block_admin(request):
            messages.error(request, "Admin users are not allowed to verify.")
            return redirect("election_list")

        election = self._get_election(uuid)

        if not election.is_voting_open():
            messages.error(request, "Voting is not open.")
            return redirect("election_detail", uuid=election.uuid)

        return render(request, self.template_name, {
            "election": election,
        })

    def post(self, request, uuid):
        if self._block_admin(request):
            messages.error(request, "Admin users are not allowed to verify.")
            return redirect("election_list")

        election = self._get_election(uuid)

        if not election.is_voting_open():
            messages.error(request, "Voting is not open.")
            return redirect("election_detail", uuid=election.uuid)

        action = request.POST.get("action")

        if action == "send_otp":
            return self._handle_send_otp(request, election)

        if action == "verify_otp":
            return self._handle_verify_otp(request, election)

        messages.error(request, "Invalid request.")
        return redirect("verify_voter", uuid=election.uuid)

    def _handle_send_otp(self, request, election):
        vid = normalize_vid(request.POST.get("vid", ""))
        phone = normalize_phone(request.POST.get("phone", ""))

        if not vid or not phone:
            messages.error(request, "VID and mobile number are required.")
            return redirect("verify_voter", uuid=election.uuid)

        voter = self._find_voter(election, vid)

        if not voter:
            messages.error(request, "Invalid VID.")
            return redirect("verify_voter", uuid=election.uuid)

        try:
            real_phone = decrypt_text(voter.phone_encrypted)
        except Exception:
            messages.error(request, "Phone data error.")
            return redirect("verify_voter", uuid=election.uuid)

        if phone != real_phone:
            messages.error(request, "Mobile number does not match this VID.")
            return redirect("verify_voter", uuid=election.uuid)

        voter_hash = voter.voter_id_hash

        if self._already_voted(election, voter_hash):
            messages.error(request, "You have already voted.")
            return redirect("election_detail", uuid=election.uuid)

        ElectionVoterSession.objects.get_or_create(
            election=election,
            user=request.user,
            defaults={"eligible_voter": voter}
        )

        otp = generate_otp()

        VoterVerification.objects.create(
            election=election,
            eligible_voter=voter,
            voter_hash=voter_hash,
            otp_hash=sha256_hash(otp),
            otp_verified=False,
            attempts=0,
            expires_at=VoterVerification.default_expiry(),
        )

        print(f"[DEV OTP] VID={vid} PHONE={phone} OTP={otp}")

        request.session["pending_vid"] = vid

        messages.success(request, "OTP sent (check console).")
        return render(request, self.template_name, {
            "election": election,
            "otp_sent": True,
            "vid": vid,
        })

    def _handle_verify_otp(self, request, election):
        vid = request.session.get("pending_vid")
        otp = request.POST.get("otp")

        if not vid or not otp:
            messages.error(request, "Session expired.")
            return redirect("verify_voter", uuid=election.uuid)

        voter = self._find_voter(election, vid)

        if not voter:
            messages.error(request, "Invalid VID.")
            return redirect("verify_voter", uuid=election.uuid)

        verification = VoterVerification.objects.filter(
            election=election,
            eligible_voter=voter,
            otp_verified=False,
        ).order_by("-created").first()

        if not verification:
            messages.error(request, "OTP not found.")
            return redirect("verify_voter", uuid=election.uuid)

        if verification.is_expired():
            messages.error(request, "OTP expired.")
            return redirect("verify_voter", uuid=election.uuid)

        verification.attempts += 1

        if verification.otp_hash != sha256_hash(otp):
            verification.save(update_fields=["attempts"])
            messages.error(request, "Invalid OTP.")
            return redirect("verify_voter", uuid=election.uuid)

        verification.otp_verified = True
        verification.verified_at = timezone.now()
        verification.save()

        request.session["verified_voter_id"] = voter.id
        request.session["verified_voter_hash"] = voter.voter_id_hash
        request.session.pop("pending_vid", None)

        messages.success(request, "Verification successful.")
        return redirect("vote", uuid=election.uuid)