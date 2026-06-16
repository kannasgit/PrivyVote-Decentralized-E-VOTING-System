from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.conf import settings

from app.views.registration import VoterRegistrationView
from app.views.registration_otp import RegistrationOTPVerifyView

from app.views import (
    index, profile, terms, privacy, accessibility, contact, faqs, how,
    ElectionListView, ElectionDetailView, ElectionCreateView, ElectionUpdateView,
    CandidateCreateView, CandidateUpdateView, CandidateDeleteView, CandidateDetailView,
    VoteView, StartElectionView, CloseElectionView, VoterVerificationView,
    OpenRegistrationView, CloseRegistrationView,
)

admin.site.site_header = "Election Management System"
admin.site.site_title = "PrivyVote"

urlpatterns = [
    path("", index, name="index"),
    path("profile/", profile, name="profile"),
    path("terms/", terms, name="terms"),
    path("privacy/", privacy, name="privacy"),
    path("accessibility/", accessibility, name="accessibility"),
    path("contact/", contact, name="contact"),
    path("faqs/", faqs, name="faqs"),
    path("how/", how, name="how"),

    path("elections/", ElectionListView.as_view(), name="election_list"),
    path("elections/create/", ElectionCreateView.as_view(), name="create_election"),
    path("elections/<uuid:uuid>/", ElectionDetailView.as_view(), name="election_detail"),
    path("elections/<uuid:uuid>/edit/", ElectionUpdateView.as_view(), name="edit_election"),
    path("elections/<uuid:uuid>/start/", StartElectionView.as_view(), name="start_election"),
    path("elections/<uuid:uuid>/close/", CloseElectionView.as_view(), name="close_election"),
    path("elections/<uuid:uuid>/open-registration/", OpenRegistrationView.as_view(), name="open_registration"),
    path("elections/<uuid:uuid>/close-registration/", CloseRegistrationView.as_view(), name="close_registration"),

    path("elections/<uuid:uuid>/register/", VoterRegistrationView.as_view(), name="voter_registration"),
    path("elections/<uuid:uuid>/register/verify-otp/", RegistrationOTPVerifyView.as_view(), name="registration_otp_verify"),
    path("elections/<uuid:uuid>/verify/", VoterVerificationView.as_view(), name="verify_voter"),
    path("elections/<uuid:uuid>/vote/", VoteView.as_view(), name="vote"),

    path("elections/<uuid:uuid>/candidates/create/", CandidateCreateView.as_view(), name="add_candidate"),
    path("candidates/<uuid:uuid>/", CandidateDetailView.as_view(), name="candidate_detail"),
    path("candidates/<uuid:uuid>/edit/", CandidateUpdateView.as_view(), name="edit_candidate"),
    path("candidates/<uuid:uuid>/delete/", CandidateDeleteView.as_view(), name="delete_candidate"),

    path("accounts/", include("allauth.urls")),

    path("admin/", admin.site.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)