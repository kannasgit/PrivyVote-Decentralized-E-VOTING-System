from .base import index, profile, terms, privacy, accessibility, contact, faqs, how
from .auth import CustomLoginView

from .election import (
    ElectionListView,
    ElectionDetailView,
    ElectionCreateView,
    ElectionUpdateView,
    OpenRegistrationView,
    CloseRegistrationView,
    StartElectionView,
    CloseElectionView,
)

from .candidate import (
    CandidateCreateView,
    CandidateUpdateView,
    CandidateDeleteView,
    CandidateDetailView,
)

from .vote import VoteView
from .voter_verification import VoterVerificationView
from .registration import VoterRegistrationView