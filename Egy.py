import ecdsa
import hashlib
import base58
import signal
import atexit
import sys

def generate_bitcoin_address():
    private_key = ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)
    public_key = private_key.get_verifying_key()

    public_key_bytes = public_key.to_string()
    sha256_hash = hashlib.sha256(public_key_bytes).digest()
    ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

    network_byte = b'\x00'  # Mainnet
    extended_ripemd160_hash = network_byte + ripemd160_hash
    checksum = hashlib.sha256(hashlib.sha256(extended_ripemd160_hash).digest()).digest()[:4]

    bitcoin_address = base58.b58encode(extended_ripemd160_hash + checksum).decode('utf-8')

    return private_key.to_string().hex(), public_key.to_string().hex(), bitcoin_address

def cleanup():
    print("Cleaning up before exit...")
    # Perform cleanup tasks here

atexit.register(cleanup)

def signal_handler(sig, frame):
    print(f"Received signal {sig}. Exiting gracefully...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def save_data_to_file(file_path, private_key, public_key, address):
    with open(file_path, 'a') as file:
        file.write(f"Private Key: {private_key}\n")
        file.write(f"Public Key: {public_key}\n")
        file.write(f"Bitcoin Address: {address}\n")
        file.write("=" * 40 + "\n")

if __name__ == "__main__":
    addresses_file = "b.txt"
    existing_addresses = set()
    try:
        with open(addresses_file, 'r') as file:
            existing_addresses = set(line.strip() for line in file)

        while True:
            private_key, public_key, bitcoin_address = generate_bitcoin_address()

            if bitcoin_address in existing_addresses:
                print("Match found! Bitcoin Address:", bitcoin_address)
                new_data_file = "Matched_Bitcoin_data.txt"
                save_data_to_file(new_data_file, private_key, public_key, bitcoin_address)
            else:
                print("Generated Bitcoin Address:", bitcoin_address)

    except KeyboardInterrupt:
        print("Script stopped by user.")
