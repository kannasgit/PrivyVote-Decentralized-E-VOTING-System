from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from app.models import Election, Vote, EligibleVoter
from app.forms import ElectionForm, ElectionUpdateForm


# -------------------------------
# LIST VIEW
# -------------------------------
class ElectionListView(ListView):
    model = Election
    template_name = "app/elections/list.html"
    context_object_name = "elections"
    paginate_by = 10

    def get_queryset(self):
        return Election.objects.all().select_related("created_by")


# -------------------------------
# DETAIL VIEW
# -------------------------------
class ElectionDetailView(DetailView):
    model = Election
    template_name = "app/elections/detail.html"
    context_object_name = "election"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def _get_verified_voter(self, request, election):
        voter_id = request.session.get("verified_voter_id")
        voter_hash = request.session.get("verified_voter_hash")

        if not voter_id or not voter_hash:
            return None

        return EligibleVoter.objects.filter(
            id=voter_id,
            election=election,
            voter_id_hash=voter_hash,
            is_active=True,
            is_registered=True,
        ).first()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        election = self.get_object()

        # Basic info
        vote_results = election.get_results()
        election_status = election.get_status()
        candidates = election.get_ordered_candidates()

        # Permissions
        user = self.request.user
        can_manage = (
            user.is_authenticated and (
                user.is_superuser
                or user.is_staff
                or election.created_by == user
            )
        )

        can_edit = can_manage and election.is_editable()

        # Verified voter session
        verified_voter = self._get_verified_voter(self.request, election)
        is_verified = verified_voter is not None

        # Voting check
        voted = False
        if verified_voter:
            voted = Vote.objects.filter(
                election=election,
                voter_hash=verified_voter.voter_id_hash
            ).exists()

        # FINAL voting permission
        can_vote = (
            election.is_voting_open()
            and is_verified
            and not voted
        )

        context.update({
            "voted": voted,
            "can_edit": can_edit,
            "can_vote": can_vote,
            "can_manage": can_manage,
            "is_verified": is_verified,
            "verified_voter": verified_voter,
            "vote_results": vote_results,
            "election_status": election_status,
            "candidates": candidates,
            "results_available": election.can_show_results(),
        })

        return context


# -------------------------------
# CREATE
# -------------------------------
class ElectionCreateView(LoginRequiredMixin, CreateView):
    model = Election
    form_class = ElectionForm
    template_name = "app/elections/create.html"

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        messages.success(self.request, "Election created successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("election_detail", kwargs={"uuid": self.object.uuid})


# -------------------------------
# UPDATE
# -------------------------------
class ElectionUpdateView(LoginRequiredMixin, UpdateView):
    model = Election
    form_class = ElectionUpdateForm
    template_name = "app/elections/edit.html"
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def dispatch(self, request, *args, **kwargs):
        election = self.get_object()

        allowed = (
            request.user.is_superuser
            or request.user.is_staff
            or election.created_by == request.user
        )

        if not allowed:
            messages.error(request, "No permission.")
            return redirect("election_detail", uuid=election.uuid)

        if not election.is_editable():
            messages.error(request, "Election cannot be edited.")
            return redirect("election_detail", uuid=election.uuid)

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        messages.success(self.request, "Election updated successfully.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("election_detail", kwargs={"uuid": self.object.uuid})


# -------------------------------
# BASE ADMIN CHECK (REUSABLE)
# -------------------------------
def is_admin(user, election):
    return (
        user.is_superuser
        or user.is_staff
        or election.created_by == user
    )


# -------------------------------
# REGISTRATION CONTROL
# -------------------------------
class OpenRegistrationView(LoginRequiredMixin, View):
    def post(self, request, uuid):
        election = get_object_or_404(Election, uuid=uuid)

        if not is_admin(request.user, election):
            messages.error(request, "No permission.")
            return redirect("election_detail", uuid=election.uuid)

        if election.open_registration():
            messages.success(request, "Registration opened.")
        else:
            messages.error(request, "Failed to open registration.")

        return redirect("election_detail", uuid=election.uuid)


class CloseRegistrationView(LoginRequiredMixin, View):
    def post(self, request, uuid):
        election = get_object_or_404(Election, uuid=uuid)

        if not is_admin(request.user, election):
            messages.error(request, "No permission.")
            return redirect("election_detail", uuid=election.uuid)

        if election.close_registration():
            messages.success(request, "Registration closed.")
        else:
            messages.error(request, "Failed to close registration.")

        return redirect("election_detail", uuid=election.uuid)


# -------------------------------
# ELECTION CONTROL
# -------------------------------
class StartElectionView(LoginRequiredMixin, View):
    def post(self, request, uuid):
        election = get_object_or_404(Election, uuid=uuid)

        if not is_admin(request.user, election):
            messages.error(request, "No permission.")
            return redirect("election_detail", uuid=election.uuid)

        if election.start_election():
            messages.success(request, "Election started.")
        else:
            messages.error(request, "Failed to start election.")

        return redirect("election_detail", uuid=election.uuid)


class CloseElectionView(LoginRequiredMixin, View):
    def post(self, request, uuid):
        election = get_object_or_404(Election, uuid=uuid)

        if not is_admin(request.user, election):
            messages.error(request, "No permission.")
            return redirect("election_detail", uuid=election.uuid)

        try:
            if election.close_election():
                messages.success(request, "Election closed & results generated.")
            else:
                messages.error(request, "Failed to close election.")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")

        return redirect("election_detail", uuid=election.uuid)