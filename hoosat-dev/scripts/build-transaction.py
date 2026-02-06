#!/usr/bin/env python3
"""
Hoosat Transaction Builder

Builds and signs Hoosat transactions using the REST API.
Supports mainnet and testnet networks.

Usage:
    python build-transaction.py --from ADDRESS --to ADDRESS --amount AMOUNT

Example:
    python build-transaction.py \
        --from hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe \
        --to hoosat:qqkqkzjvr7zwxxmjxjkmxx \
        --amount 1.5 \
        --private-key YOUR_PRIVATE_KEY \
        --network mainnet
"""

import argparse
import json
import sys
from typing import List, Dict, Optional, Tuple

try:
    import requests
except ImportError:
    print("Error: requests library not found. Install with: pip install requests")
    sys.exit(1)


class HoosatTransactionBuilder:
    """Build and submit Hoosat transactions."""
    
    NETWORKS = {
        'mainnet': {
            'api_url': 'https://proxy.hoosat.net/api/v1',
            'prefix': 'hoosat:'
        },
        'testnet': {
            'api_url': 'https://proxy.hoosat.net/api/v1',  # Same API for both
            'prefix': 'hoosattest:'
        }
    }
    
    def __init__(self, network: str = 'mainnet'):
        """Initialize builder with network."""
        if network not in self.NETWORKS:
            raise ValueError(f"Invalid network: {network}")
        self.network = network
        self.config = self.NETWORKS[network]
        self.api_url = self.config['api_url']
    
    def validate_address(self, address: str) -> bool:
        """Validate Hoosat address."""
        return address.startswith(self.config['prefix'])
    
    def get_utxos(self, address: str) -> List[Dict]:
        """Get UTXOs for an address."""
        response = requests.post(
            f"{self.api_url}/address/utxos",
            json={'addresses': [address]}
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get UTXOs: {response.text}")
        
        data = response.json()
        if not data.get('success'):
            raise Exception(f"API error: {data.get('error')}")
        
        return data['data']['utxos']
    
    def get_balance(self, address: str) -> int:
        """Get balance for an address in sompi."""
        response = requests.get(
            f"{self.api_url}/address/{address}/balance"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get balance: {response.text}")
        
        data = response.json()
        if not data.get('success'):
            raise Exception(f"API error: {data.get('error')}")
        
        return int(data['data']['balance'])
    
    def get_fee_estimate(self) -> Dict:
        """Get fee estimate from network."""
        response = requests.get(
            f"{self.api_url}/mempool/fee-estimate"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get fee estimate: {response.text}")
        
        data = response.json()
        if not data.get('success'):
            raise Exception(f"API error: {data.get('error')}")
        
        return data['data']
    
    def select_utxos(self, utxos: List[Dict], amount_needed: int) -> Tuple[List[Dict], int]:
        """Select UTXOs to cover amount (simple selection)."""
        selected = []
        total = 0
        
        # Sort by amount (largest first for fewer inputs)
        sorted_utxos = sorted(utxos, key=lambda u: int(u['utxoEntry']['amount']), reverse=True)
        
        for utxo in sorted_utxos:
            selected.append(utxo)
            total += int(utxo['utxoEntry']['amount'])
            
            if total >= amount_needed:
                break
        
        if total < amount_needed:
            raise Exception(f"Insufficient funds. Need: {amount_needed}, Have: {total}")
        
        return selected, total
    
    def build_transaction(
        self,
        sender_address: str,
        recipient_address: str,
        amount_htn: float,
        private_key: str,
        fee_rate: Optional[str] = None
    ) -> Dict:
        """Build a transaction (simplified - actual signing would need crypto libs)."""
        # Validate addresses
        if not self.validate_address(sender_address):
            raise Exception(f"Invalid sender address: {sender_address}")
        if not self.validate_address(recipient_address):
            raise Exception(f"Invalid recipient address: {recipient_address}")
        
        # Get UTXOs
        utxos = self.get_utxos(sender_address)
        
        if not utxos:
            raise Exception("No UTXOs available for this address")
        
        # Convert amount to sompi (1 HTN = 100,000,000 sompi)
        amount_sompi = int(amount_htn * 100_000_000)
        
        # Get fee estimate
        fee_estimate = self.get_fee_estimate()
        
        if fee_rate is None:
            # Use normal bucket fee rate
            fee_rate = str(fee_estimate['normalBucket']['feeRate'])
        
        # Estimate fee (simplified calculation)
        # Actual fee calculation depends on transaction size
        estimated_fee = int(fee_rate) * 200  # Rough estimate for 200 byte tx
        
        # Select UTXOs
        total_needed = amount_sompi + estimated_fee
        selected_utxos, total_input = self.select_utxos(utxos, total_needed)
        
        # Build inputs
        inputs = []
        for utxo in selected_utxos:
            inputs.append({
                'previousOutpoint': utxo['outpoint'],
                'signatureScript': '',  # To be signed
                'sequence': 0,
                'sigOpCount': 1
            })
        
        # Build outputs
        outputs = []
        
        # Recipient output
        outputs.append({
            'amount': str(amount_sompi),
            'scriptPublicKey': {
                'scriptPublicKey': '',  # Would be derived from address
                'version': 0
            }
        })
        
        # Change output (if any)
        change = total_input - amount_sompi - estimated_fee
        if change > 1000:  # Dust threshold
            outputs.append({
                'amount': str(change),
                'scriptPublicKey': {
                    'scriptPublicKey': '',  # Would be sender's script
                    'version': 0
                }
            })
        
        # Build transaction
        transaction = {
            'version': 0,
            'inputs': inputs,
            'outputs': outputs,
            'lockTime': '0',
            'subnetworkId': '0000000000000000000000000000000000000000',
            'gas': '0',
            'payload': ''
        }
        
        return {
            'transaction': transaction,
            'fee': estimated_fee,
            'total_input': total_input,
            'change': change if change > 1000 else 0,
            'unsigned': True
        }
    
    def submit_transaction(self, signed_transaction: Dict) -> str:
        """Submit a signed transaction to the network."""
        response = requests.post(
            f"{self.api_url}/transaction/submit",
            json=signed_transaction
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to submit transaction: {response.text}")
        
        data = response.json()
        if not data.get('success'):
            raise Exception(f"API error: {data.get('error')}")
        
        return data['data']['transactionId']
    
    def get_transaction_status(self, tx_id: str) -> Dict:
        """Get transaction status."""
        response = requests.get(
            f"{self.api_url}/transaction/{tx_id}/status"
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to get status: {response.text}")
        
        data = response.json()
        if not data.get('success'):
            raise Exception(f"API error: {data.get('error')}")
        
        return data['data']


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Build and submit Hoosat transactions'
    )
    parser.add_argument(
        '--from', '-f',
        dest='sender',
        required=True,
        help='Sender address (hoosat:...)'
    )
    parser.add_argument(
        '--to', '-t',
        dest='recipient',
        required=True,
        help='Recipient address (hoosat:...)'
    )
    parser.add_argument(
        '--amount', '-a',
        type=float,
        required=True,
        help='Amount in HTN'
    )
    parser.add_argument(
        '--network', '-n',
        choices=['mainnet', 'testnet'],
        default='mainnet',
        help='Network type (default: mainnet)'
    )
    parser.add_argument(
        '--private-key',
        help='Private key for signing (hex or WIF)'
    )
    parser.add_argument(
        '--fee',
        help='Fee rate (optional, auto-estimated if not provided)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Build transaction without submitting'
    )
    parser.add_argument(
        '--status',
        help='Get status of transaction ID'
    )
    parser.add_argument(
        '--utxos',
        action='store_true',
        help='List UTXOs for sender address'
    )
    parser.add_argument(
        '--output', '-o',
        help='Save unsigned transaction to file'
    )
    
    args = parser.parse_args()
    
    builder = HoosatTransactionBuilder(args.network)
    
    # Get transaction status
    if args.status:
        try:
            status = builder.get_transaction_status(args.status)
            print(f"Transaction: {args.status}")
            print(f"Status: {status['status']}")
            if status.get('confirmingBlockHash'):
                print(f"Confirming Block: {status['confirmingBlockHash']}")
                print(f"Blue Score: {status['confirmingBlockBlueScore']}")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        return
    
    # List UTXOs
    if args.utxos:
        try:
            utxos = builder.get_utxos(args.sender)
            print(f"UTXOs for {args.sender}:")
            total = 0
            for i, utxo in enumerate(utxos, 1):
                amount = int(utxo['utxoEntry']['amount'])
                total += amount
                htn = amount / 100_000_000
                print(f"  {i}. TX: {utxo['outpoint']['transactionId']}")
                print(f"     Index: {utxo['outpoint']['index']}")
                print(f"     Amount: {htn} HTN ({amount} sompi)")
            print(f"\nTotal: {total / 100_000_000} HTN ({total} sompi)")
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        return
    
    # Build transaction
    try:
        print(f"Building transaction on {args.network}...")
        print(f"From: {args.sender}")
        print(f"To: {args.recipient}")
        print(f"Amount: {args.amount} HTN")
        
        result = builder.build_transaction(
            args.sender,
            args.recipient,
            args.amount,
            args.private_key or '',
            args.fee
        )
        
        print(f"\nTransaction built successfully!")
        print(f"Inputs: {len(result['transaction']['inputs'])}")
        print(f"Outputs: {len(result['transaction']['outputs'])}")
        print(f"Estimated Fee: {result['fee']} sompi")
        print(f"Total Input: {result['total_input']} sompi")
        if result['change'] > 0:
            print(f"Change: {result['change']} sompi")
        
        if args.dry_run:
            print("\nDry run - transaction not submitted")
            print("\nUnsigned transaction:")
            print(json.dumps(result['transaction'], indent=2))
            
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result['transaction'], f, indent=2)
                print(f"\nSaved to: {args.output}")
        else:
            if not args.private_key:
                print("\nError: Private key required to submit transaction")
                print("Use --dry-run to build unsigned transaction")
                print("Or use --output to save for offline signing")
                sys.exit(1)
            
            # Note: Actual signing would require secp256k1 and proper crypto
            # This is a placeholder - real implementation needs crypto libraries
            print("\n⚠️  Note: This script builds unsigned transactions.")
            print("   Full signing requires secp256k1 library and proper key handling.")
            print("   For production use, integrate with hoosat-sdk or hoosat-sdk-web.")
            
            # Save unsigned transaction
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(result['transaction'], f, indent=2)
                print(f"\nUnsigned transaction saved to: {args.output}")
                print("   Sign and submit using the Hoosat SDK.")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
