from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404

from app.models import Election


class CloseElectionView(LoginRequiredMixin, View):
    def post(self, request, uuid):
        election = get_object_or_404(Election, uuid=uuid)

        allowed = (
            request.user.is_superuser
            or request.user.is_staff
            or election.created_by == request.user
        )

        if not allowed:
            messages.error(request, "You do not have permission to close this election.")
            return redirect("election_detail", uuid=election.uuid)

        if election.closed_at:
            messages.warning(request, "This election is already closed.")
            return redirect("election_detail", uuid=election.uuid)

        election.close_election()
        messages.success(request, "Election closed and final tally generated.")
        return redirect("election_detail", uuid=election.uuid)