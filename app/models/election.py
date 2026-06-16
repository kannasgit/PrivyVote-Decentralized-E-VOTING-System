import uuid
import json

from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from app.encryption import Encryption, Ciphertext


class Election(models.Model):
    uuid = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True
    )

    name = models.CharField(max_length=100)
    description = models.TextField()

    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    created_by = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="created_elections",
        null=True,
        blank=True
    )

    # Election cryptographic keys
    private_key = models.TextField(null=True, blank=True, editable=False)
    public_key = models.TextField(default="", editable=False)

    # Lifecycle
    active = models.BooleanField(default=False)
    registration_open = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    registration_opened_at = models.DateTimeField(null=True, blank=True)
    registration_closed_at = models.DateTimeField(null=True, blank=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # One-time tally state
    tally_done = models.BooleanField(default=False)
    final_results = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self):
        return self.name

    # ---------------------------
    # VALIDATION
    # ---------------------------

    def clean(self):
        if self.start_date and self.end_date and self.end_date <= self.start_date:
            raise ValidationError("End date must be after start date.")

    # ---------------------------
    # SAVE
    # ---------------------------

    def save(self, *args, **kwargs):
        # Generate keypair only once
        if not self.public_key:
            encryption = Encryption()
            private_key, public_key = encryption.generate_keys()
            self.private_key = private_key
            self.public_key = public_key

        super().save(*args, **kwargs)

    # ---------------------------
    # STATUS
    # ---------------------------

    def is_registration_open(self):
        return self.registration_open and not self.active and not self.closed_at

    def is_voting_open(self):
        now = timezone.now()
        return (
            self.active
            and not self.registration_open
            and not self.closed_at
            and self.start_date <= now <= self.end_date
        )

    def get_status(self):
        now = timezone.now()

        if self.closed_at:
            return "closed"
        if self.registration_open:
            return "registration_open"
        if self.active and self.start_date <= now <= self.end_date:
            return "open"
        if now < self.start_date:
            return "scheduled"
        if now > self.end_date:
            return "expired"
        return "inactive"

    def can_show_results(self):
        return self.tally_done and bool(self.final_results)

    def is_editable(self):
        return (
            not self.started_at
            and not self.closed_at
            and not self.tally_done
            and not self.registration_open
        )

    # ---------------------------
    # LIFECYCLE
    # ---------------------------

    def open_registration(self):
        if self.closed_at or self.active or self.tally_done:
            return False

        self.registration_open = True

        if not self.registration_opened_at:
            self.registration_opened_at = timezone.now()

        self.save(update_fields=["registration_open", "registration_opened_at"])
        return True

    def close_registration(self):
        if not self.registration_open:
            return False

        self.registration_open = False
        self.registration_closed_at = timezone.now()
        self.save(update_fields=["registration_open", "registration_closed_at"])
        return True

    def start_election(self):
        now = timezone.now()

        if self.closed_at or self.tally_done:
            return False

        if self.active:
            return False

        if self.registration_open:
            return False

        if self.end_date <= self.start_date:
            return False

        if now > self.end_date:
            return False

        self.active = True

        if not self.started_at:
            self.started_at = now

        self.save(update_fields=["active", "started_at"])
        return True

    def close_election(self):
        if self.closed_at:
            return False

        self.active = False
        self.registration_open = False
        self.closed_at = timezone.now()

        self._finalize_results()

        self.save(update_fields=[
            "active",
            "registration_open",
            "closed_at",
            "final_results",
            "tally_done",
            "private_key",
        ])
        return True

    # ---------------------------
    # BALLOT ORDER
    # ---------------------------

    def get_ordered_candidates(self):
        return list(self.candidates.order_by("id"))

    # ---------------------------
    # HOMOMORPHIC TALLY HELPERS
    # ---------------------------

    def _parse_ballot(self, encrypted_ballot, expected_len):
        ballot = json.loads(encrypted_ballot)

        if not isinstance(ballot, list):
            raise ValueError("Ballot must be a list.")

        if len(ballot) != expected_len:
            raise ValueError("Ballot size mismatch.")

        parsed = []
        for value in ballot:
            parsed.append(Ciphertext(int(value)))

        return parsed

    def _tally_encrypted(self):
        """
        Homomorphic addition of encrypted ballots.
        """
        candidates = self.get_ordered_candidates()
        votes = self.votes.all()

        if not candidates:
            return None

        encryption = Encryption(public_key=self.public_key)

        totals = None
        valid_votes = 0
        rejected_votes = 0

        for vote in votes:
            try:
                ballot = self._parse_ballot(
                    vote.encrypted_ballot,
                    len(candidates)
                )

                if totals is None:
                    totals = ballot
                else:
                    new_totals = []
                    for i in range(len(ballot)):
                        new_totals.append(
                            encryption.add(totals[i], ballot[i])
                        )
                    totals = new_totals

                valid_votes += 1

            except Exception:
                rejected_votes += 1

        return {
            "totals": totals,
            "valid_votes": valid_votes,
            "rejected_votes": rejected_votes,
        }

    # ---------------------------
    # FINAL ONE-TIME DECRYPT
    # ---------------------------

    def _finalize_results(self):
        """
        One-time decrypt after homomorphic aggregation.
        """
        if self.tally_done:
            return

        tally = self._tally_encrypted()
        candidates = self.get_ordered_candidates()

        if tally is None or tally["totals"] is None:
            self.final_results = json.dumps({
                "totals": [0] * len(candidates),
                "valid_votes": 0,
                "rejected_votes": 0,
            })
            self.tally_done = True
            self.private_key = None
            return

        encryption = Encryption(
            public_key=self.public_key,
            private_key=self.private_key
        )

        decrypted_totals = []

        for ct in tally["totals"]:
            decrypted_totals.append(encryption.decrypt(ct))

        self.final_results = json.dumps({
            "totals": decrypted_totals,
            "valid_votes": tally["valid_votes"],
            "rejected_votes": tally["rejected_votes"],
        })

        self.tally_done = True

        # Destroy private key after final one-time tally
        self.private_key = None

    # ---------------------------
    # PUBLIC RESULTS
    # ---------------------------

    def get_results(self):
        if not self.can_show_results():
            return None

        data = json.loads(self.final_results)
        totals = data.get("totals", [])

        candidates = self.get_ordered_candidates()
        total_votes = sum(totals)

        results = []
        for candidate, vote_count in zip(candidates, totals):
            percentage = (vote_count / total_votes * 100) if total_votes else 0
            results.append({
                "candidate": candidate,
                "votes": vote_count,
                "percentage": round(percentage, 2),
            })

        results.sort(key=lambda item: item["votes"], reverse=True)

        return {
            "results": results,
            "total_votes": total_votes,
            "valid_votes": data.get("valid_votes", 0),
            "rejected_votes": data.get("rejected_votes", 0),
            "winner": results[0] if results else None,
        }