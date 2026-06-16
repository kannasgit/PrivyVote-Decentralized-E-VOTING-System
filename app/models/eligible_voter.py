import random
import string
from django.db import models
from app.models import Election


def generate_vid():
    return "PV-" + "".join(random.choices(string.digits, k=8))


class EligibleVoter(models.Model):
    election = models.ForeignKey(
        Election,
        on_delete=models.CASCADE,
        related_name="eligible_voters"
    )

    voter_id = models.CharField(max_length=20, db_index=True, null=True, blank=True)
    voter_id_hash = models.CharField(max_length=256, db_index=True)

    full_name = models.CharField(max_length=150)
    phone_encrypted = models.TextField()
    phone_last2 = models.CharField(max_length=2)

    is_active = models.BooleanField(default=True)
    is_registered = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created"]
        unique_together = ("election", "voter_id")

    def save(self, *args, **kwargs):
        if not self.voter_id:
            while True:
                vid = generate_vid()
                if not EligibleVoter.objects.filter(
                    election=self.election,
                    voter_id=vid
                ).exists():
                    self.voter_id = vid
                    break

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.election.name} - {self.voter_id}"