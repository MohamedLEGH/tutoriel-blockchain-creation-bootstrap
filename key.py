from os import urandom  # Should be a good source of entropy
from base58 import b58encode, b58decode  # for Bitcoin encoding
import hashlib  # for Bitcoin hashing
import json

import coincurve  # faster than ecdsa to compute public key from private key

max_32bitvalue = 0xffffffff
bitcoin_wifprefix = 0x80
bitcoin_addrprefix = 0x00


def curveorder():
    maxval = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
    return maxval


def gen_private_key():
    # max value of the eliptic curve

    maxval = curveorder()
    p = urandom(32)  # almost any 32 random bytes array is a private key
    pint = int.from_bytes(p, 'big')

    while(pint > maxval or pint < 0):  # a private key cannot be zero (or below)
        # and should be lower than the maximal value of the eliptic curve
        p = urandom(32)
        pint = int.from_bytes(p, 'big')
    return p


def priv_to_pub(key, compressed=True):
    return coincurve.PublicKey.from_secret(key).format(compressed=compressed)


def priv_to_pub_raw(key):  # only for ecdsa-secp256k1 curve
    return priv_to_pub(key, compressed=False)[1:]


def pub_to_pub(pub, compressed=True):
    return coincurve.PublicKey(pub).format(compressed=compressed)


class Account:

    def __init__(self, private=None):
        if(private is None):  # need to check type of input (bytes only)
            private = gen_private_key()
        self.pk = private
        self.curve = "ecdsa-secp256k1"

    @classmethod
    def fromhex(cls, hexa):  # need to check type of input (str only)
        return cls(bytes.fromhex(hexa))

    @classmethod
    def fromfile(cls, file_name):
        with open(file_name) as json_file:
            data = json.load(json_file)
            return cls.fromhex(data["private_key"])

    def private_key(self):
        return self.pk.hex()

    def to_file(self, file_name):
        key = {"private_key": self.private_key()}
        with open(file_name, 'w') as key_file:
            json.dump(key, key_file)

    def sign(self, message):
        signature = coincurve.PrivateKey(
            self.pk).sign_recoverable(message.encode())
        return signature


def hash256(x): return hashlib.sha256(x).digest()


def doublehash(x): return hash256(hash256(x))


def ripemd160(x): return hashlib.new('ripemd160', data=x).digest()


def hash160(x): return ripemd160(hash256(x))


def wif_to_priv(wif, compressed=True):
    pkeychecked = b58decode(wif).decode()  # convert to base58

    # remove firt byte (network flag)
    # and last 4 bytes (checksum)
    # or last 5 bytes for compressed because of the compressed byte flag
    return pkeychecked[1:-5] if compressed else pkeychecked[1:-4]


def public_to_P2PKH(public_key, compressed=True, network_addrprefix=bitcoin_wifprefix):
    public = pub_to_pub(public_key, compressed=True)
    encrypted_pub = bytes([network_addrprefix]) + hash160(public)
    check = doublehash(encrypted_pub)
    checksum = check[:4]
    address = encrypted_pub + checksum
    return b58encode(address).decode()


class BitcoinAccount(Account):
    network_wifprefix = bitcoin_wifprefix
    network_addrprefix = bitcoin_addrprefix

    def __init__(self, private=None):
        super().__init__(private)

    @classmethod
    def fromwif(cls, wif):
        return cls(wif_to_priv(wif))

    def to_file(self, file_name=None):
        if(file_name == None):
            file_name = self.to_address() + ".json"
        super().to_file(file_name)  #  check parameter less

    def to_wif(self, compressed=True):
        s1 = bytes([self.network_wifprefix]) + self.pk
        if(compressed):
            s1 += bytes([0x01])  # add compressed flag byte
        checksum = doublehash(s1)[:4]  # first 4 bytes = checksum
        wif = s1 + checksum
        return b58encode(wif).decode()

    def to_pub(self, compressed=True):
        public = priv_to_pub(self.pk, compressed)
        return public

    def to_P2PKH(self, compressed=True):
        pub = self.to_pub(compressed=compressed)
        return public_to_P2PKH(pub, compressed=True, network_addrprefix=self.network_wifprefix)

    def to_address(self, compressed=True):
        return self.to_P2PKH(compressed=compressed)

    def __repr__(self, compressed=True):
        string_val = "WIF: " + str(self.to_wif(compressed)) + "\n" + \
            "Address: " + self.to_address(compressed)
        return string_val


def verify_signature(signature, message, address):
    public_key = coincurve.PublicKey.from_signature_and_message(
        bytes.fromhex(signature), message.encode()).format()
    address_computed = public_to_P2PKH(public_key)
    return address_computed == address
