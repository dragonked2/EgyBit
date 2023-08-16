import bitcoin
from bitcoin import privtopub, pubtoaddr, encode_privkey
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
        private_key_hex = bitcoin.random_key()
        private_key_wif = encode_privkey(private_key_hex, 'wif')
        public_key_hex = privtopub(private_key_hex)
        bitcoin_address = pubtoaddr(public_key_hex)
        
        print("Private Key (Hex):", private_key_hex)
        print("Private Key (WIF):", private_key_wif)
        print("Bitcoin Address:", bitcoin_address)
        
        if check_for_match(bitcoin_address, addresses_to_match):
            save_to_file(output_file, private_key_hex, private_key_wif, bitcoin_address)
            print("Data saved to bitcoin_addresses.txt")

if __name__ == "__main__":
    with open("filter.txt", "r") as file:
        addresses_to_match = set(file.read().splitlines())

    def signal_handler(sig, frame):
        global exit_flag
        exit_flag = True
        print("Ctrl+C detected. Exiting gracefully...")
    signal.signal(signal.SIGINT, signal_handler)

    with open("bitcoin_addresses.txt", "a") as output_file:
        process_addresses(addresses_to_match, output_file)

    print("Script has been gracefully terminated.")
