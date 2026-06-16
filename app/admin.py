from django.contrib import admin
from .models import Election, Candidate, Vote, EligibleVoter, VoterVerification,ElectionVoterSession


@admin.register(Election)
class ElectionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "registration_open",
        "active",
        "start_date",
        "end_date",
        "created",
        "registration_opened_at",
        "registration_closed_at",
        "started_at",
        "closed_at",
    )
    list_filter = (
        "registration_open",
        "active",
        "created",
        "start_date",
        "end_date",
    )
    search_fields = ("name", "description")
    readonly_fields = (
        "created",
        "registration_opened_at",
        "registration_closed_at",
        "started_at",
        "closed_at",
        "public_key",
        "private_key",
    )


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("get_display_name", "election", "get_party_name", "created")
    list_filter = ("election",)
    search_fields = ("user__username",)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = (
        "uuid",
        "election",
        "voter_hash",
        "short_ballot",
        "created",
    )
    search_fields = ("voter_hash", "election__name")
    list_filter = ("election", "created")
    readonly_fields = (
        "uuid",
        "election",
        "voter_hash",
        "encrypted_ballot",
        "created",
    )

    def short_ballot(self, obj):
        return obj.encrypted_ballot[:50] + "..." if obj.encrypted_ballot else ""

    short_ballot.short_description = "Encrypted Ballot"


@admin.register(EligibleVoter)
class EligibleVoterAdmin(admin.ModelAdmin):
    list_display = (
        "election",
        "voter_id",
        "voter_id_hash",
        "full_name",
        "phone_last2",
        "is_active",
        "is_registered",
        "created",
    )
    list_filter = ("election", "is_active", "is_registered", "created")
    search_fields = ("voter_id", "voter_id_hash", "full_name")
    readonly_fields = ("created",)
    
@admin.register(ElectionVoterSession)
class ElectionVoterSessionAdmin(admin.ModelAdmin):
    list_display = ("user", "election", "eligible_voter", "created")
    list_filter = ("election", "created")
    search_fields = ("user__username",)

@admin.register(VoterVerification)
class VoterVerificationAdmin(admin.ModelAdmin):
    list_display = (
        "election",
        "eligible_voter",
        "voter_hash",
        "otp_verified",
        "attempts",
        "expires_at",
        "created",
        "verified_at",
    )
    list_filter = ("election", "otp_verified", "created", "verified_at")
    search_fields = ("voter_hash",)
    readonly_fields = ("created", "verified_at")