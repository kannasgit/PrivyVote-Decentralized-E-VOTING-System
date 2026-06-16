from phe import paillier
import json

# Generate keypair
public_key, private_key = paillier.generate_paillier_keypair(n_length=1024)

# Extract public components
n = public_key.n
g = public_key.g

print("\n=== PUBLIC KEY (Use in JS) ===")
print("n =", n)
print("g =", g)

# Save public key to file (for JS use later)
with open("public_key.json", "w") as f:
    json.dump({"n": str(n), "g": str(g)}, f)

# Save private key securely (temporary for testing)
with open("private_key.json", "w") as f:
    json.dump({
        "p": str(private_key.p),
        "q": str(private_key.q)
    }, f)

print("\nKeys saved to public_key.json and private_key.json")