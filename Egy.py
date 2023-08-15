import ecdsa
import os
import hashlib
import base58
from bitcoin import *

def generate_and_check(private_key, existing_addresses, total_generated):
    signing_key = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
    verifying_key = signing_key.get_verifying_key()
    public_key = b"\x04" + verifying_key.to_string()
    sha256_hash = hashlib.sha256(public_key).digest()
    address_hash = hashlib.sha256(sha256_hash).hexdigest()

    ripemd160_hash = hashlib.new("ripemd160", sha256_hash).digest()
    bitcoin_address = base58.b58encode_check(b"\x00" + ripemd160_hash).decode()
    
    # Calculate Wallet Import Format (WIF) manually
    version = b'\x80'  # Mainnet private key prefix
    private_key_bytes = private_key
    extended_key = version + private_key_bytes
    checksum = hashlib.sha256(hashlib.sha256(extended_key).digest()).digest()[:4]
    wif = base58.b58encode(extended_key + checksum).decode()

    status = "Generated Bitcoin Address: {}".format(bitcoin_address)
    if bitcoin_address in existing_addresses:
        status += " (Match found!)"

        with open('bito.txt', 'a') as match_file:
            match_file.write("Private Key (Hex): {}\n".format(private_key.hex()))
            match_file.write("Bitcoin Address: {}\n".format(bitcoin_address))
            match_file.write("WIF: {}\n".format(wif))
            match_file.write("\n")

    print(status)
    print("Total Addresses Generated:", total_generated)

def main():
    with open('output1.txt', 'r') as file:
        existing_addresses = [line.strip() for line in file]

    total_generated = 0

    while True:
        private_key = os.urandom(32)
        generate_and_check(private_key, existing_addresses, total_generated)
        total_generated += 1



if __name__ == "__main__":
    main()
