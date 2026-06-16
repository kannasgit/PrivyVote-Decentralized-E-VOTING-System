from app.services.vote_audit_service import log_vote_to_blockchain
import json

from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404

from app.models import Election, Vote, EligibleVoter, ElectionVoterSession
from app.encryption import Encryption


class VoteView(LoginRequiredMixin, View):
    template_name = "app/voting/vote.html"

    def _block_admin(self, request):
        return request.user.is_authenticated and request.user.is_staff

    def _get_election(self, uuid):
        return get_object_or_404(Election, uuid=uuid)

    def _build_plain_ballot(self, selected_index, candidates_count):
        return [1 if i == selected_index else 0 for i in range(candidates_count)]

    def _encrypt_ballot(self, election, ballot):
        encryption = Encryption(public_key=election.public_key)
        encrypted = []

        for value in ballot:
            ct = encryption.encrypt(value)
            encrypted.append(str(ct.ciphertext))

        return encrypted

    def _get_verified_voter(self, request, election):
        voter_id = request.session.get("verified_voter_id")
        voter_hash = request.session.get("verified_voter_hash")

        if not voter_id or not voter_hash:
            return None

        voter = EligibleVoter.objects.filter(
            id=voter_id,
            election=election,
            voter_id_hash=voter_hash,
            is_active=True,
            is_registered=True,
        ).first()

        if not voter:
            return None

        linked = ElectionVoterSession.objects.filter(
            election=election,
            user=request.user,
            eligible_voter=voter,
        ).exists()

        if not linked:
            return None

        return voter

    def _already_voted(self, election, voter_hash):
        return Vote.objects.filter(
            election=election,
            voter_hash=voter_hash
        ).exists()

    def get(self, request, uuid):
        if self._block_admin(request):
            messages.error(request, "Admin users are not allowed to vote.")
            return redirect("election_list")

        election = self._get_election(uuid)

        if not election.is_voting_open():
            messages.error(request, "Voting is not open.")
            return redirect("election_detail", uuid=election.uuid)

        voter = self._get_verified_voter(request, election)
        if not voter:
            messages.error(request, "Please complete voter verification before voting.")
            return redirect("verify_voter", uuid=election.uuid)

        voter_hash = voter.voter_id_hash
        if self._already_voted(election, voter_hash):
            messages.error(request, "You have already voted.")
            return redirect("election_detail", uuid=election.uuid)

        return render(request, self.template_name, {
            "election": election,
            "candidates": election.get_ordered_candidates(),
        })

    def post(self, request, uuid):
        if self._block_admin(request):
            messages.error(request, "Admin users are not allowed to vote.")
            return redirect("election_list")

        election = self._get_election(uuid)

        if not election.is_voting_open():
            messages.error(request, "Voting is not open.")
            return redirect("election_detail", uuid=election.uuid)

        voter = self._get_verified_voter(request, election)
        if not voter:
            messages.error(request, "Please complete voter verification before voting.")
            return redirect("verify_voter", uuid=election.uuid)

        voter_hash = voter.voter_id_hash
        if self._already_voted(election, voter_hash):
            messages.error(request, "You have already voted.")
            return redirect("election_detail", uuid=election.uuid)

        selected_index_raw = request.POST.get("candidate_choice")
        if selected_index_raw is None:
            messages.error(request, "Please select a candidate.")
            return redirect("vote", uuid=election.uuid)

        candidates = election.get_ordered_candidates()
        candidates_count = len(candidates)

        try:
            selected_index = int(selected_index_raw)
        except (TypeError, ValueError):
            messages.error(request, "Invalid candidate selection.")
            return redirect("vote", uuid=election.uuid)

        if selected_index < 0 or selected_index >= candidates_count:
            messages.error(request, "Invalid candidate selection.")
            return redirect("vote", uuid=election.uuid)

        plain_ballot = self._build_plain_ballot(selected_index, candidates_count)
        encrypted_ballot = self._encrypt_ballot(election, plain_ballot)

        vote = Vote.objects.create(
            election=election,
            voter_hash=voter_hash,
            encrypted_ballot=json.dumps(encrypted_ballot),
        )

        # 🔥 blockchain audit (add this)
        try:
            audit_result = log_vote_to_blockchain(
                election_id=str(election.uuid),
                voter_ref=str(voter_hash),
                vote_payload=json.dumps(encrypted_ballot),
            )
            print("Blockchain audit stored:", audit_result)
        except Exception as e:
            print("Blockchain audit failed:", str(e))

        request.session.pop("verified_voter_id", None)
        request.session.pop("verified_voter_hash", None)

        messages.success(request, "Your vote has been securely recorded.")
        return redirect("election_detail", uuid=election.uuid)