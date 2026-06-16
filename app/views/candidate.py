"""
Class-based views for Candidate model operations
"""
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy

from django.contrib.auth.models import User
from app.models import Candidate, Election, Profile
from app.forms import CandidateForm


class CandidateMixin:
    """Shared methods for candidate views"""

    def _can_manage(self, user, election):
        """Check if user can add/edit/remove candidates"""
        return user.is_authenticated and (
            user.is_superuser or user == election.created_by or user.is_election_manager()
        )

    def _check_editable(self, election, redirect_url):
        """Ensure election is editable (not active or closed)"""
        if not election.is_editable():
            if election.closed_at:
                messages.error(self.request, "Cannot modify candidates in a closed election.")
            else:
                messages.error(self.request, "Cannot modify candidates during active voting period.")
            return redirect(redirect_url)
        return None


class CandidateCreateView(LoginRequiredMixin, CandidateMixin, CreateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'app/candidates/create.html'

    def dispatch(self, request, *args, **kwargs):
        self.election = get_object_or_404(Election, uuid=kwargs['uuid'])
        if not self._can_manage(request.user, self.election):
            messages.error(request, "You don't have permission to add candidates.")
            return redirect('election_list')
        redirect_resp = self._check_editable(self.election, redirect('election_detail', uuid=self.election.uuid))
        if redirect_resp:
            return redirect_resp
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.election = self.election
        response = super().form_valid(form)
        Profile.objects.get_or_create(user=self.object.user)
        messages.success(
            self.request,
            f"Candidate '{self.object.user.get_full_name()}' has been added to the election!"
        )
        return response

    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'uuid': self.election.uuid})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        existing_users = Candidate.objects.filter(election=self.election).values_list('user_id', flat=True)
        available_users = User.objects.filter(is_active=True, groups__name='Candidates').exclude(id__in=existing_users)
        context['no_candidates_available'] = available_users.count() == 0
        return context

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['election'] = self.election
        return kwargs


class CandidateUpdateView(LoginRequiredMixin, CandidateMixin, UpdateView):
    model = Candidate
    form_class = CandidateForm
    template_name = 'app/candidates/edit.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def dispatch(self, request, *args, **kwargs):
        self.election = self.get_object().election
        if not self._can_manage(request.user, self.election):
            messages.error(request, "You don't have permission to edit candidates.")
            return redirect('election_list')
        redirect_resp = self._check_editable(self.election, redirect('candidate_detail', uuid=self.get_object().uuid))
        if redirect_resp:
            return redirect_resp
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"Candidate '{self.object.user.get_full_name()}' has been updated successfully!"
        )
        return response

    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'uuid': self.election.uuid})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        return context


class CandidateDeleteView(LoginRequiredMixin, CandidateMixin, DeleteView):
    model = Candidate
    template_name = 'app/candidates/delete.html'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def dispatch(self, request, *args, **kwargs):
        self.election = self.get_object().election
        if not self._can_manage(request.user, self.election):
            messages.error(request, "You don't have permission to remove candidates.")
            return redirect('election_detail', uuid=self.election.uuid)
        redirect_resp = self._check_editable(self.election, redirect('candidate_detail', uuid=self.get_object().uuid))
        if redirect_resp:
            return redirect_resp
        return super().dispatch(request, *args, **kwargs)

    def delete(self, request, *args, **kwargs):
        candidate_name = str(self.get_object())
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f"Candidate '{candidate_name}' has been removed from the election.")
        return response

    def get_success_url(self):
        return reverse_lazy('election_detail', kwargs={'uuid': self.election.uuid})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['election'] = self.election
        return context


class CandidateDetailView(LoginRequiredMixin, CandidateMixin, DetailView):
    model = Candidate
    template_name = 'app/candidates/detail.html'
    context_object_name = 'candidate'
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        candidate = self.get_object()
        election = candidate.election
        context['election'] = election

        from app.models import Vote
        from app.encryption import sha256_hash

        if self.request.user.is_authenticated:
         voter_hash = sha256_hash(self.request.user.email.strip().lower())
         user_votes = Vote.objects.filter(election=election, voter_hash=voter_hash)
         context['voted'] = user_votes.count()
         context['can_remove_candidate'] = self._can_manage(self.request.user, election)
        else:
         context['voted'] = 0
         context['can_remove_candidate'] = False

        return context