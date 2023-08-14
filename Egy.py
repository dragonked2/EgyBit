import ecdsa
import hashlib
import base58
import signal
import atexit
import sys
import logging

class BitcoinAddressGenerator:
    def __init__(self):
        self.existing_addresses = set()
        self.addresses_file = "b.txt"
        self.new_data_file = "Matched_Bitcoin_data.txt"
        self.setup_existing_addresses()

    def setup_existing_addresses(self):
        try:
            with open(self.addresses_file, 'r') as file:
                self.existing_addresses = set(line.strip() for line in file)
        except FileNotFoundError:
            pass

    def generate_private_key(self):
        return ecdsa.SigningKey.generate(curve=ecdsa.SECP256k1)

    def derive_public_key(self, private_key):
        return private_key.get_verifying_key()

    def calculate_bitcoin_address(self, public_key):
        public_key_bytes = public_key.to_string()
        sha256_hash = hashlib.sha256(public_key_bytes).digest()
        ripemd160_hash = hashlib.new('ripemd160', sha256_hash).digest()

        network_byte = b'\x00'
        extended_ripemd160_hash = network_byte + ripemd160_hash
        checksum = hashlib.sha256(hashlib.sha256(extended_ripemd160_hash).digest()).digest()[:4]

        bitcoin_address = base58.b58encode(extended_ripemd160_hash + checksum).decode('utf-8')
        return bitcoin_address

    def save_data_to_file(self, private_key, public_key, address):
        with open(self.new_data_file, 'a') as file:
            file.write(f"Private Key: {private_key}\n")
            file.write(f"Public Key: {public_key}\n")
            file.write(f"Bitcoin Address: {address}\n")
            file.write("=" * 40 + "\n")

    def generate_bitcoin_address(self):
        private_key = self.generate_private_key()
        public_key = self.derive_public_key(private_key)
        bitcoin_address = self.calculate_bitcoin_address(public_key)
        return private_key.to_string().hex(), public_key.to_string().hex(), bitcoin_address

    def main_loop(self):
        generated_count = 0
        match_count = 0

        print("Loaded", len(self.existing_addresses), "addresses from", self.addresses_file)
        
        while True:
            private_key, public_key, bitcoin_address = self.generate_bitcoin_address()
            generated_count += 1

            if bitcoin_address in self.existing_addresses:
                match_count += 1
                print(f"Match found! Bitcoin Address: {bitcoin_address}")
                self.save_data_to_file(private_key, public_key, bitcoin_address)
            else:
                print(f"Generated Bitcoin Address ({generated_count} total): {bitcoin_address}")
            
            if generated_count % 1000 == 0:
                print(f"Generated {generated_count} addresses, {match_count} matches")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    generator = BitcoinAddressGenerator()

    def cleanup():
        logging.info("Cleaning up before exit...")
        # Perform cleanup tasks here

    atexit.register(cleanup)

    def signal_handler(sig, frame):
        logging.info(f"Received signal {sig}. Exiting gracefully...")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        generator.main_loop()
    except KeyboardInterrupt:
        logging.info("Script stopped by user.")
