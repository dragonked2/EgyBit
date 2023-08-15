import ecdsa
import hashlib
import base58
import secrets
from bitcoin import *

def generate_and_check(private_key, existing_addresses):
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    verifying_key = signing_key.get_verifying_key()
    public_key = b"\x04" + verifying_key.to_string()
    sha256_hash = hashlib.sha256(public_key).digest()
    ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()
    bitcoin_address = base58.b58encode_check(b"\x00" + ripemd160_hash).decode()

    if bitcoin_address in existing_addresses:
        wif = base58.b58encode_check(b"\x80" + private_key).decode()
        match_info = (
            "Private Key (Hex): {}\n".format(private_key.hex()),
            "Bitcoin Address: {}\n".format(bitcoin_address),
            "WIF: {}\n".format(wif),
            "\n"
        )

        with open('matches.txt', 'a') as matches_file:
            matches_file.writelines(match_info)
            matches_file.flush()

        print("Generated Bitcoin Address: {} (Match found!)".format(bitcoin_address))
    else:
        print("Generated Bitcoin Address:", bitcoin_address)

def main():
    with open('output1.txt', 'r') as file:
        existing_addresses = {line.strip() for line in file}

    while True:
        private_key = secrets.token_bytes(32)
        generate_and_check(private_key, existing_addresses)


if __name__ == "__main__":
    main()
