"""
Base views for general functionality like homepage and profile
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from app.models import Election, Vote, Invitation
from app.encryption import sha256_hash


def index(request):
    """Homepage view showing election summary and ongoing elections"""
    all_elections = Election.objects.all().select_related('created_by')

    ongoing_elections = []
    upcoming_elections = []
    recently_closed_elections = []

    for election in all_elections:
        if election.is_voting_open():
            ongoing_elections.append(election)
        elif not election.active and election.start_date > election.created:
            upcoming_elections.append(election)
        elif election.closed_at:
            recently_closed_elections.append(election)

    ongoing_elections.sort(key=lambda x: x.end_date)
    featured_elections = ongoing_elections[:4]

    if len(featured_elections) < 4:
        remaining_slots = 4 - len(featured_elections)
        upcoming_elections.sort(key=lambda x: x.start_date)
        featured_elections.extend(upcoming_elections[:remaining_slots])

    context = {
        'elections': featured_elections,
        'ongoing_elections': ongoing_elections,
        'upcoming_elections': upcoming_elections[:3],
        'recently_closed_elections': recently_closed_elections[:3],
        'elections_count': {
            'ongoing': len(ongoing_elections),
            'upcoming': len(upcoming_elections),
            'recently_closed': len(recently_closed_elections),
            'total': len(all_elections)
        }
    }
    return render(request, 'app/index.html', context)


@login_required
def profile(request):
    """User profile view showing their voting history, created elections, and invitations"""
    # Use hashed email for vote lookup
    voter_hash = sha256_hash(request.user.email)
    votes = Vote.objects.filter(voter_hash=voter_hash).select_related('election')

    # Elections created by this user
    created_elections = Election.objects.filter(created_by=request.user).order_by('-created')
    for election in created_elections:
        election.can_edit = election.is_editable() if hasattr(election, 'is_editable') else False

    # Invitations addressed to this user's email
    invitations = Invitation.objects.filter(invited_email=request.user.email).select_related('election').order_by('-created_at')
    pending_invitations = invitations.filter(status='pending')
    accepted_invitations = invitations.filter(status='accepted')
    declined_invitations = invitations.filter(status='declined')

    context = {
        'votes': votes,
        'created_elections': created_elections,
        'invitations': invitations,
        'pending_invitations': pending_invitations,
        'accepted_invitations': accepted_invitations,
        'declined_invitations': declined_invitations,
        'invitation_counts': {
            'total': invitations.count(),
            'pending': pending_invitations.count(),
            'accepted': accepted_invitations.count(),
            'declined': declined_invitations.count(),
        }
    }
    return render(request, 'app/profile.html', context)


# ---------------------------
# Legal Pages
# ---------------------------

def terms(request):
    return render(request, 'app/legal/terms.html')


def privacy(request):
    return render(request, 'app/legal/privacy.html')


def accessibility(request):
    return render(request, 'app/legal/accessibility.html')


def contact(request):
    if request.method == 'POST':
        messages.success(request, 'Thank you for your message. We will get back to you within 24-48 hours.')
        return redirect('contact')
    return render(request, 'app/legal/contact.html')


def faqs(request):
    return render(request, 'app/legal/faqs.html')


def how(request):
    return render(request, 'app/how.html')