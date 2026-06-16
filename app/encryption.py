from lightphe.cryptosystems.Paillier import Paillier
from sympy import mod_inverse
import hashlib
import json


class Ciphertext:
    """Wrapper for encrypted value with optional randomness."""

    def __init__(self, ciphertext: int, randomness: int = None):
        self.ciphertext = ciphertext
        self.randomness = randomness

    def __repr__(self):
        return f"Ciphertext(ciphertext={self.ciphertext}, randomness={self.randomness})"

    def to_json(self) -> str:
        return json.dumps({
            "ciphertext": str(self.ciphertext),
            "randomness": str(self.randomness) if self.randomness else None
        })

    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        randomness = int(data["randomness"]) if data["randomness"] else None
        return cls(int(data["ciphertext"]), randomness)


class Encryption:
    """Paillier homomorphic encryption wrapper using lightphe."""

    def __init__(self, public_key: str = None, private_key: str = None):

        # Fresh instance (for generating keys)
        if public_key is None and private_key is None:
            self.paillier = Paillier()
            return

        # Keys stored in DB as JSON strings
        pub = json.loads(public_key) if isinstance(public_key, str) else public_key
        priv = json.loads(private_key) if isinstance(private_key, str) else private_key

        keys = {"public_key": pub}

        if priv:
            keys["private_key"] = priv

        self.paillier = Paillier(keys)

    # --------------------------------------------------
    # Key Management
    # --------------------------------------------------

    def generate_keys(self, key_size=1024):
        """
        Generate full Paillier keypair.
        Returns (private_key_json, public_key_json)
        """
        self.paillier.generate_keys(key_size)

        public_key = self.paillier.keys["public_key"]
        private_key = self.paillier.keys["private_key"]

        return json.dumps(private_key), json.dumps(public_key)

    # --------------------------------------------------
    # Encryption / Decryption
    # --------------------------------------------------

    def encrypt(self, plaintext: int, rand: int = None) -> Ciphertext:
        if rand is None:
            rand = self.paillier.generate_random_key()

        ct = self.paillier.encrypt(plaintext, rand)
        return Ciphertext(ct, rand)

    def decrypt(self, ct: Ciphertext) -> int:
        if "private_key" not in self.paillier.keys:
            raise ValueError("Private key not loaded for decryption")

        return self.paillier.decrypt(ct.ciphertext)

    # --------------------------------------------------
    # Homomorphic Addition
    # --------------------------------------------------

    def add(self, ct1: Ciphertext, ct2: Ciphertext) -> Ciphertext:
        sum_ct = self.paillier.add(ct1.ciphertext, ct2.ciphertext)

        combined_rand = None
        if ct1.randomness and ct2.randomness:
            combined_rand = (
                ct1.randomness * ct2.randomness
            ) % self.paillier.ciphertext_modulo

        return Ciphertext(sum_ct, combined_rand)

    # --------------------------------------------------
    # Utilities
    # --------------------------------------------------

    def hash(self, data: str) -> str:
        return hashlib.sha256(data.encode()).hexdigest()

    def verify_zero(self, ct: Ciphertext) -> bool:
        if "private_key" not in self.paillier.keys:
            raise ValueError("Private key required")

        n = self.paillier.plaintext_modulo
        lambda_n = self.paillier.keys["private_key"]["lambda"]

        m = mod_inverse(n, lambda_n)
        r = pow(ct.ciphertext, m, n)

        test_ct = self.encrypt(0, r)
        return test_ct.ciphertext == ct.ciphertext
    
def sha256_hash(text: str) -> str:
    """Return SHA-256 hash of the input string"""
    return hashlib.sha256(text.encode('utf-8')).hexdigest()


import random
import string
from cryptography.fernet import Fernet
from django.conf import settings


def normalize_vid(vid: str) -> str:
    return "".join(str(vid).split()).upper()


def normalize_phone(phone: str) -> str:
    digits = "".join(ch for ch in str(phone) if ch.isdigit())
    if len(digits) == 12 and digits.startswith("91"):
        return digits[2:]
    return digits


def generate_otp(length: int = 6) -> str:
    return "".join(random.choice(string.digits) for _ in range(length))


def get_fernet():
    return Fernet(settings.FIELD_ENCRYPTION_KEY.encode())


def encrypt_text(text: str) -> str:
    return get_fernet().encrypt(text.encode("utf-8")).decode("utf-8")


def decrypt_text(token: str) -> str:
    return get_fernet().decrypt(token.encode("utf-8")).decode("utf-8")