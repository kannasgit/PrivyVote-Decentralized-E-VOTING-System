import json
from pathlib import Path

from django.conf import settings
from web3 import Web3


BASE_DIR = Path(settings.BASE_DIR)
BLOCKCHAIN_DIR = BASE_DIR / "blockchain"

ABI_PATH = BLOCKCHAIN_DIR / "contractABI.json"
ADDRESS_PATH = BLOCKCHAIN_DIR / "contractAddress.txt"


def get_web3():
    return Web3(Web3.HTTPProvider("http://127.0.0.1:7545"))


def get_contract():
    with open(ABI_PATH, "r", encoding="utf-8") as f:
        abi = json.load(f)

    with open(ADDRESS_PATH, "r", encoding="utf-8") as f:
        contract_address = f.read().strip()

    web3 = get_web3()
    contract = web3.eth.contract(
        address=Web3.to_checksum_address(contract_address),
        abi=abi,
    )
    return web3, contract


def store_vote_hash_on_chain(vote_hash_hex: str):
    web3, contract = get_contract()

    sender_address = web3.eth.accounts[0]

    if vote_hash_hex.startswith("0x"):
        vote_hash_hex = vote_hash_hex[2:]

    if len(vote_hash_hex) != 64:
        raise ValueError("Vote hash must be 32 bytes / 64 hex characters.")

    vote_hash_bytes = bytes.fromhex(vote_hash_hex)

    tx_hash = contract.functions.storeVote(vote_hash_bytes).transact({
        "from": sender_address
    })

    receipt = web3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "tx_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
        "status": receipt.status,
    }


def get_on_chain_vote_count():
    web3, contract = get_contract()
    return contract.functions.getCount().call()