from datetime import timedelta

from django.db import models
from django.utils import timezone

from app.models import Election, EligibleVoter


class VoterVerification(models.Model):
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="verifications"
    )

    eligible_voter = models.ForeignKey(
    EligibleVoter,
    on_delete=models.CASCADE,
    related_name="verifications",
    null=True,
    blank=True,
    )

    voter_hash = models.CharField(max_length=256, db_index=True)

    otp_hash = models.CharField(max_length=256, null=True, blank=True)
    otp_verified = models.BooleanField(default=False)

    attempts = models.PositiveIntegerField(default=0)
    max_attempts = models.PositiveIntegerField(default=5)

    created = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def is_expired(self):
        return timezone.now() > self.expires_at

    @staticmethod
    def default_expiry():
        return timezone.now() + timedelta(minutes=5)

    def __str__(self):
        state = "verified" if self.otp_verified else "pending"
        return f"{self.election.name} - {self.eligible_voter_id} - {state}"