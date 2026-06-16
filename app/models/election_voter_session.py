from django.db import models
from django.contrib.auth.models import User

from app.models import Election, EligibleVoter


class ElectionVoterSession(models.Model):
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="voter_sessions",
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="election_voter_sessions",
    )
    eligible_voter = models.ForeignKey(
        EligibleVoter,
        on_delete=models.CASCADE,
        related_name="linked_sessions",
    )
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("election", "user")

    def __str__(self):
        return f"{self.user.username} - {self.election.name}"