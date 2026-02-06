#!/usr/bin/env python3
"""
Hoosat Address Generator

Generates Hoosat addresses with their corresponding private keys.
Supports mainnet and testnet networks.
Uses BLAKE3 hashing (Hoosat-specific, not kHash like Kaspa).
Uses Hoosat custom bech32 format with ':' separator.

Usage:
    python generate-address.py [--network mainnet|testnet] [--count 1]

Example:
    python generate-address.py --network mainnet --count 3
    python generate-address.py --validate hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe
"""

import argparse
import hashlib
import os
import secrets
import sys
from typing import Tuple, Optional, List

# Hoosat Bech32 Constants
CHARSET = 'qpzry9x8gf2tvdw0s3jn54khce6mua7l'
CHECKSUM_LENGTH = 8
GENERATOR = [0x98f2bc8e61, 0x79b76d99e2, 0xf33e5fb3c4, 0xae2eabe2a8, 0x1e4f43e470]

try:
    import blake3
except ImportError:
    print("Warning: blake3 library not found. Install with: pip install blake3")
    blake3 = None

try:
    import secp256k1
except ImportError:
    secp256k1 = None

try:
    from ecdsa import SigningKey, SECP256k1
except ImportError:
    SigningKey = None
    SECP256k1 = None

if secp256k1 is None and SigningKey is None:
    print("Error: Either secp256k1 or ecdsa library required. Install with:")
    print("  pip install ecdsa  (recommended - pure Python, no compilation)")
    print("  pip install secp256k1  (requires compilation)")
    sys.exit(1)


def hoosat_bech32_encode(prefix: str, payload: bytes) -> str:
    """Encode to Hoosat bech32 format with ':' separator."""
    # Prepend version byte (0x01 for ECDSA)
    data = bytes([0x01]) + payload
    
    # Convert from 8-bit to 5-bit
    converted = convert_bits(data, 8, 5, True)
    
    # Calculate checksum
    checksum = calculate_checksum(prefix, converted)
    combined = converted + checksum
    
    # Encode to base32
    base32_string = encode_to_base32(combined)
    
    return f"{prefix}:{base32_string}"


def hoosat_bech32_decode(encoded: str):
    """Decode Hoosat bech32 address."""
    # Validation
    if len(encoded) < CHECKSUM_LENGTH + 2:
        raise ValueError(f"Invalid bech32 string length {len(encoded)}")
    
    # Work with lowercase
    normalized = encoded.lower()
    
    # Find last colon
    colon_index = normalized.rfind(':')
    if colon_index < 1 or colon_index + CHECKSUM_LENGTH + 1 > len(normalized):
        raise ValueError('Invalid index of ":"')
    
    # Split prefix and data
    prefix = normalized[:colon_index]
    data_string = normalized[colon_index + 1:]
    
    # Decode from base32
    decoded = decode_from_base32(data_string)
    
    # Verify checksum
    if not verify_checksum(prefix, decoded):
        raise ValueError("Checksum failed")
    
    # Remove checksum (last 8 bytes)
    data_without_checksum = decoded[:-CHECKSUM_LENGTH]
    
    # Convert from 5-bit to 8-bit
    converted = convert_bits(data_without_checksum, 5, 8, False)
    
    # Extract version and payload
    version = converted[0]
    payload = bytes(converted[1:])
    
    return prefix, payload, version


def convert_bits(data, from_bits, to_bits, pad):
    """Convert between bit groups."""
    regrouped = []
    next_byte = 0
    filled_bits = 0
    
    for value in data:
        next_byte = (next_byte << from_bits) | value
        filled_bits += from_bits
        
        while filled_bits >= to_bits:
            regrouped.append((next_byte >> (filled_bits - to_bits)) & ((1 << to_bits) - 1))
            filled_bits -= to_bits
    
    if pad and filled_bits > 0:
        regrouped.append((next_byte << (to_bits - filled_bits)) & ((1 << to_bits) - 1))
    
    return regrouped


def calculate_checksum(prefix: str, data: List[int]) -> bytes:
    """Calculate bech32 checksum."""
    # Create checksum generator state
    polymod = 1
    
    # Process prefix
    for char in prefix:
        polymod = polymod_step(polymod, ord(char) & 0x1f)
    polymod = polymod_step(polymod, 0)
    
    # Process data
    for value in data:
        polymod = polymod_step(polymod, value)
    
    # Finalize
    for _ in range(CHECKSUM_LENGTH):
        polymod = polymod_step(polymod, 0)
    
    # Return checksum bytes
    checksum = []
    for i in range(CHECKSUM_LENGTH):
        checksum.append((polymod >> (5 * (7 - i))) & 0x1f)
    
    return bytes(checksum)


def polymod_step(prev: int, value: int) -> int:
    """Single step of checksum polymod."""
    b = prev >> 35
    c = ((prev & 0x7ffffffff) << 5) ^ value
    
    for i in range(len(GENERATOR)):
        if (b >> i) & 1:
            c ^= GENERATOR[i]
    
    return c


def verify_checksum(prefix: str, data: bytes) -> bool:
    """Verify bech32 checksum."""
    try:
        calculated = calculate_checksum(prefix, list(data[:-CHECKSUM_LENGTH]))
        return list(data[-CHECKSUM_LENGTH:]) == list(calculated)
    except:
        return False


def encode_to_base32(data: bytes) -> str:
    """Encode bytes to base32 string using CHARSET."""
    return ''.join(CHARSET[b] for b in data)


def decode_from_base32(s: str) -> bytes:
    """Decode base32 string to bytes."""
    result = []
    for char in s.lower():
        if char not in CHARSET:
            raise ValueError(f"Invalid character '{char}'")
        result.append(CHARSET.index(char))
    return bytes(result)


class HoosatAddressGenerator:
    """Generate Hoosat addresses and keys."""
    
    NETWORK_PREFIXES = {
        'mainnet': 'hoosat',
        'testnet': 'hoosattest'
    }
    
    def __init__(self, network: str = 'mainnet'):
        """Initialize generator with network type."""
        if network not in self.NETWORK_PREFIXES:
            raise ValueError(f"Invalid network: {network}")
        self.network = network
        self.prefix = self.NETWORK_PREFIXES[network]
    
    def generate_private_key(self) -> bytes:
        """Generate a random 32-byte private key."""
        return secrets.token_bytes(32)
    
    def private_key_to_wif(self, private_key: bytes, compressed: bool = True) -> str:
        """Convert private key to Wallet Import Format (WIF)."""
        # Add version byte (0x80 for mainnet, 0xEF for testnet)
        version_byte = b'\x80' if self.network == 'mainnet' else b'\xef'
        
        # Add private key
        extended = version_byte + private_key
        
        # Add compression flag if needed
        if compressed:
            extended += b'\x01'
        
        # Double SHA256 checksum
        checksum = hashlib.sha256(hashlib.sha256(extended).digest()).digest()[:4]
        
        # Base58 encode
        try:
            import base58
            return base58.b58encode(extended + checksum).decode('ascii')
        except ImportError:
            print("Error: base58 library not found. Install with: pip install base58")
            sys.exit(1)
    
    def wif_to_private_key(self, wif: str) -> bytes:
        """Convert WIF to private key."""
        try:
            import base58
            decoded = base58.b58decode(wif)
            
            # Check checksum
            payload = decoded[:-4]
            checksum = decoded[-4:]
            calculated_checksum = hashlib.sha256(hashlib.sha256(payload).digest()).digest()[:4]
            
            if checksum != calculated_checksum:
                raise ValueError("Invalid WIF checksum")
            
            # Remove version byte and compression flag
            if len(payload) == 33:  # Uncompressed
                return payload[1:]
            elif len(payload) == 34:  # Compressed
                return payload[1:-1]
            else:
                raise ValueError("Invalid WIF length")
        except ImportError:
            print("Error: base58 library not found. Install with: pip install base58")
            sys.exit(1)
    
    def private_key_to_public_key(self, private_key: bytes, compressed: bool = True) -> bytes:
        """Convert private key to public key using secp256k1 or ecdsa."""
        if secp256k1 is not None:
            # Use secp256k1 library (C extension, faster)
            privkey = secp256k1.PrivateKey(private_key)
            pubkey = privkey.pubkey
            
            if compressed:
                return pubkey.serialize()
            else:
                return pubkey.serialize(compressed=False)
        
        elif SigningKey is not None:
            # Use ecdsa library (pure Python, no compilation needed)
            sk = SigningKey.from_string(private_key, curve=SECP256k1)
            vk = sk.verifying_key
            
            if compressed:
                # Compressed format: prefix + x-coordinate
                x = vk.to_string()[:32]
                y = vk.to_string()[32:]
                # Determine prefix based on y-coordinate parity
                prefix = b'\x02' if int.from_bytes(y, 'big') % 2 == 0 else b'\x03'
                return prefix + x
            else:
                # Uncompressed format: 0x04 + x + y
                return b'\x04' + vk.to_string()
        
        else:
            raise ImportError("Either secp256k1 or ecdsa library required for key derivation")
    
    def public_key_to_address(self, public_key: bytes) -> str:
        """Convert public key to Hoosat address using BLAKE3 and custom bech32."""
        # BLAKE3 hash of public key (Hoosat uses BLAKE3, not SHA256 like Kaspa)
        if blake3 is not None:
            blake3_hash = blake3.blake3(public_key).digest()
        else:
            # Fallback to hashlib blake3 if available (Python 3.11+)
            try:
                blake3_hash = hashlib.blake3(public_key).digest()
            except AttributeError:
                print("Error: blake3 library required. Install with: pip install blake3")
                sys.exit(1)
        
        # Use first 20 bytes for address (similar to hash160)
        hash160 = blake3_hash[:20]
        
        # Encode with Hoosat custom bech32 (uses ':' separator)
        address = hoosat_bech32_encode(self.prefix, hash160)
        
        return address
    
    def generate_address(self, compressed: bool = True) -> Tuple[str, str, bytes]:
        """Generate a new address with its private key.
        
        Returns:
            Tuple of (address, wif_private_key, raw_private_key)
        """
        private_key = self.generate_private_key()
        public_key = self.private_key_to_public_key(private_key, compressed)
        address = self.public_key_to_address(public_key)
        wif = self.private_key_to_wif(private_key, compressed)
        
        return address, wif, private_key
    
    def validate_address(self, address: str) -> bool:
        """Validate a Hoosat address."""
        try:
            prefix, payload, version = hoosat_bech32_decode(address)
            
            # Check prefix matches network
            if prefix != self.prefix:
                return False
            
            # Check payload is valid
            if payload is None or len(payload) == 0:
                return False
            
            return True
        except Exception:
            return False
    
    def get_address_info(self, address: str) -> dict:
        """Get information about an address."""
        try:
            prefix, payload, version = hoosat_bech32_decode(address)
            
            # Determine network from prefix
            network = None
            for net, pre in self.NETWORK_PREFIXES.items():
                if prefix == pre:
                    network = net
                    break
            
            if network is None:
                return {"valid": False, "error": "Unknown prefix"}
            
            return {
                "valid": True,
                "address": address,
                "network": network,
                "prefix": prefix,
                "hash160": payload.hex(),
                "version": version
            }
        except Exception as e:
            return {"valid": False, "error": str(e)}


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Generate Hoosat addresses and private keys'
    )
    parser.add_argument(
        '--network', '-n',
        choices=['mainnet', 'testnet'],
        default='mainnet',
        help='Network type (default: mainnet)'
    )
    parser.add_argument(
        '--count', '-c',
        type=int,
        default=1,
        help='Number of addresses to generate (default: 1)'
    )
    parser.add_argument(
        '--validate', '-v',
        type=str,
        help='Validate an existing address'
    )
    parser.add_argument(
        '--uncompressed', '-u',
        action='store_true',
        help='Generate uncompressed public keys'
    )
    parser.add_argument(
        '--output', '-o',
        type=str,
        help='Output file to save results'
    )
    parser.add_argument(
        '--format', '-f',
        choices=['text', 'json', 'csv'],
        default='text',
        help='Output format (default: text)'
    )
    
    args = parser.parse_args()
    
    generator = HoosatAddressGenerator(args.network)
    
    # Validate mode
    if args.validate:
        info = generator.get_address_info(args.validate)
        
        if info["valid"]:
            print(f"✓ Valid {info['network']} address")
            print(f"  Address: {info['address']}")
            print(f"  Prefix: {info['prefix']}")
            print(f"  Hash160: {info['hash160']}")
        else:
            print(f"✗ Invalid address: {info['error']}")
        
        return
    
    # Generate mode
    results = []
    compressed = not args.uncompressed
    
    print(f"Generating {args.count} address(es) for {args.network}...\n")
    
    for i in range(args.count):
        address, wif, private_key = generator.generate_address(compressed)
        
        result = {
            'index': i + 1,
            'address': address,
            'private_key_wif': wif,
            'private_key_hex': private_key.hex(),
            'network': args.network,
            'compressed': compressed
        }
        results.append(result)
        
        # Print to console
        if args.format == 'text':
            print(f"Address {i + 1}:")
            print(f"  Address:     {address}")
            print(f"  Private Key: {wif}")
            print(f"  Hex:         {private_key.hex()}")
            print()
    
    # Save to file if specified
    if args.output:
        # Create output directory if it doesn't exist
        output_dir = os.path.dirname(args.output)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir, exist_ok=True)
        
        if args.format == 'json':
            import json
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
        elif args.format == 'csv':
            import csv
            with open(args.output, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=results[0].keys())
                writer.writeheader()
                writer.writerows(results)
        else:
            with open(args.output, 'w') as f:
                for result in results:
                    f.write(f"Address: {result['address']}\n")
                    f.write(f"Private Key: {result['private_key_wif']}\n")
                    f.write(f"Hex: {result['private_key_hex']}\n")
                    f.write("\n")
        
        print(f"Results saved to {args.output}")
    
    # Security warning
    print("⚠️  SECURITY WARNING:")
    print("   Keep your private keys secure and never share them!")
    print("   These keys are generated locally and are not stored anywhere.")
    print()
    print("   Hoosat uses BLAKE3 hashing (not kHash like Kaspa)")
    print("   Addresses start with 'hoosat:' (mainnet) or 'hoosattest:' (testnet)")


if __name__ == '__main__':
    main()
