from django.views import View
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from app.models import Election, EligibleVoter
from app.forms import VoterRegistrationForm
from app.encryption import sha256_hash, encrypt_text, normalize_phone


class VoterRegistrationView(View):
    template_name = "app/voting/voter_registration.html"

    def _get_election(self, uuid):
        return get_object_or_404(Election, uuid=uuid)

    def _block_admin(self, request):
        return request.user.is_authenticated and request.user.is_staff

    def get(self, request, uuid):
        if self._block_admin(request):
            messages.error(request, "Admin users are not allowed to register.")
            return redirect("election_list")

        election = self._get_election(uuid)

        if not election.is_registration_open():
            messages.error(request, "Registration is not open.")
            return redirect("election_detail", uuid=election.uuid)

        return render(
            request,
            self.template_name,
            {
                "election": election,
                "form": VoterRegistrationForm(),
            },
        )

    def post(self, request, uuid):
        if self._block_admin(request):
            messages.error(request, "Admin users are not allowed to register.")
            return redirect("election_list")

        election = self._get_election(uuid)

        if not election.is_registration_open():
            messages.error(request, "Registration is not open.")
            return redirect("election_detail", uuid=election.uuid)

        form = VoterRegistrationForm(request.POST)
        if not form.is_valid():
            return render(
                request,
                self.template_name,
                {
                    "election": election,
                    "form": form,
                },
            )

        full_name = form.cleaned_data["full_name"]
        phone_number = normalize_phone(form.cleaned_data["phone_number"])

        voter = EligibleVoter.objects.create(
            election=election,
            full_name=full_name,
            phone_encrypted=encrypt_text(phone_number),
            phone_last2=phone_number[-2:],
            is_active=True,
            is_registered=True,
            voter_id_hash="temp",
        )

        voter.voter_id_hash = sha256_hash(voter.voter_id)
        voter.save(update_fields=["voter_id_hash"])

        print(f"[DEV VID] Name={full_name} | Phone={phone_number} | VID={voter.voter_id}")

        messages.success(
            request,
            "Registration successful. Your Voter ID has been printed in the console."
        )
        return redirect("election_detail", uuid=election.uuid)