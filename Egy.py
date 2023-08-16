import ecdsa
import os
import hashlib
import base58
import signal

exit_flag = False

def save_to_file(file, private_key_hex, private_key_wif, bitcoin_address):
    file.write("Private Key (Hex): " + private_key_hex + "\n")
    file.write("Private Key (WIF): " + private_key_wif + "\n")
    file.write("Bitcoin Address: " + bitcoin_address + "\n")
    file.write("\n")

def check_for_match(address, addresses_to_match):
    return address in addresses_to_match

def process_addresses(addresses_to_match, output_file):
    while not exit_flag:
        # Generate a random private key
        private_key = os.urandom(32)
        private_key_hex = private_key.hex()

        # Derive public key
        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = sk.get_verifying_key()
        public_key = b'\x04' + vk.to_string()
        public_key_hex = public_key.hex()

        # Calculate Bitcoin address
        h = hashlib.sha256(public_key).digest()
        ripe = hashlib.new('ripemd160')
        ripe.update(h)
        network_byte = b'\x00'  # Mainnet
        extended_ripe = network_byte + ripe.digest()
        checksum = hashlib.sha256(hashlib.sha256(extended_ripe).digest()).digest()[:4]
        bitcoin_address = base58.b58encode(extended_ripe + checksum).decode('utf-8')

        # Convert private key to WIF format
        private_key_wif = base58.b58encode_check(b'\x80' + private_key).decode('utf-8')

        print("Private Key (Hex):", private_key_hex)
        print("Private Key (WIF):", private_key_wif)
        print("Bitcoin Address:", bitcoin_address)

        if check_for_match(bitcoin_address, addresses_to_match):
            save_to_file(output_file, private_key_hex, private_key_wif, bitcoin_address)
            print("Data saved to bitcoin_addresses.txt")

if __name__ == "__main__":
    with open("ad.txt", "r") as file:
        addresses_to_match = set(file.read().splitlines())

    def signal_handler(sig, frame):
        global exit_flag
        exit_flag = True
        print("Ctrl+C detected. Exiting gracefully...")
    signal.signal(signal.SIGINT, signal_handler)

    with open("bitcoin_addresses.txt", "a") as output_file:
        process_addresses(addresses_to_match, output_file)

    print("Script has been gracefully terminated.")
