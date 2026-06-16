import hashlib
from datetime import datetime, timezone

from app.services.blockchain_service import store_vote_hash_on_chain


def build_vote_audit_hash(election_id, voter_ref, vote_payload):
    raw = f"{election_id}|{voter_ref}|{vote_payload}|{datetime.now(timezone.utc).isoformat()}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def log_vote_to_blockchain(election_id, voter_ref, vote_payload):
    vote_hash = build_vote_audit_hash(
        election_id=election_id,
        voter_ref=voter_ref,
        vote_payload=vote_payload,
    )
    return store_vote_hash_on_chain(vote_hash)