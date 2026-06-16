from app.models import Election, EligibleVoter
from app.encryption import sha256_hash
from django.utils.crypto import get_random_string
from django.utils import timezone

now = timezone.now()

e = Election.objects.filter(
    active=True,
    closed_at__isnull=True,
    start_date__lte=now,
    end_date__gte=now
).order_by('start_date').first()

if not e:
    e = Election.objects.filter(
        active=True,
        closed_at__isnull=True,
        start_date__gt=now
    ).order_by('start_date').first()

if not e:
    print("No active or upcoming election found.")
else:
    vid = "1234567890123456"
    salt = get_random_string(32)
    voter_hash = sha256_hash(f"{vid}{salt}")

    EligibleVoter.objects.create(
        election=e,
        voter_hash=voter_hash,
        salt=salt
    )

    print("Election:", e.name)
    print("UUID:", e.uuid)
    print("VID:", vid)