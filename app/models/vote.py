import uuid
from django.db import models


class Vote(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    election = models.ForeignKey(
        'app.Election',
        on_delete=models.CASCADE,
        related_name='votes'
    )

    voter_hash = models.CharField(
        max_length=256,
        db_index=True
    )

    encrypted_ballot = models.TextField()

    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('election', 'voter_hash')
        ordering = ['-created']

    def __str__(self):
        return f"Vote {self.uuid} - {self.election.name}"