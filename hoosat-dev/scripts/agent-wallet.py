#!/usr/bin/env python3
"""
Hoosat Agent Wallet Manager

Manages encrypted wallets, address book, and agent configuration.
"""

import os
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
try:
    from .agent_crypto import AgentCrypto, SessionManager
except ImportError:
    from agent_crypto import AgentCrypto, SessionManager

# Default paths
DEFAULT_WALLET_DIR = Path.home() / '.hoosat-wallets'
WALLETS_FILE = 'wallets.enc'
CONFIG_FILE = 'config.json'
ADDRESS_BOOK_FILE = 'address-book.json'
TRANSACTION_LOG = 'transactions.log'


@dataclass
class Wallet:
    """Represents a single wallet."""
    name: str
    address: str
    private_key: str
    network: str = 'mainnet'
    created_at: float = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = time.time()


@dataclass
class AddressEntry:
    """Represents an address book entry."""
    label: str
    address: str
    network: str = 'mainnet'
    added_at: float = None
    
    def __post_init__(self):
        if self.added_at is None:
            self.added_at = time.time()


class AgentWalletManager:
    """Main wallet manager for Hoosat agent."""
    
    def __init__(self, wallet_dir: Optional[str] = None):
        """Initialize wallet manager."""
        self.wallet_dir = Path(wallet_dir) if wallet_dir else DEFAULT_WALLET_DIR
        self.wallet_dir.mkdir(parents=True, exist_ok=True)
        
        self.wallets_file = self.wallet_dir / WALLETS_FILE
        self.config_file = self.wallet_dir / CONFIG_FILE
        self.address_book_file = self.wallet_dir / ADDRESS_BOOK_FILE
        self.transaction_log = self.wallet_dir / TRANSACTION_LOG
        
        self.session = SessionManager()
        self._wallets_cache: Dict[str, Wallet] = {}
        self._address_book_cache: Dict[str, AddressEntry] = {}
        
        self._load_config()
    
    def _load_config(self):
        """Load or create default configuration."""
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = self._default_config()
            self._save_config()
    
    def _default_config(self) -> Dict:
        """Return default configuration."""
        return {
            'version': '1.0.0',
            'security': {
                'requirePasswordEvery': 'session',
                'autoLockAfter': 3600,
                'sessionTimeout': 3600
            },
            'autoApprove': {
                'enabled': False,
                'defaultMaxAmount': '100000000',  # 1 HTN
                'wallets': {}
            },
            'network': {
                'default': 'testnet',  # Start with testnet for safety
                'apiEndpoints': {
                    'mainnet': 'https://proxy.hoosat.net/api/v1',
                    'testnet': 'https://proxy.hoosat.net/api/v1'
                }
            },
            'features': {
                'dryRun': True,  # Default to dry-run mode
                'confirmTransactions': True,
                'logTransactions': True
            }
        }
    
    def _save_config(self):
        """Save configuration to file."""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def is_initialized(self) -> bool:
        """Check if wallet system is initialized."""
        return self.wallets_file.exists()
    
    def initialize(self, password: str) -> bool:
        """Initialize wallet system with master password."""
        try:
            crypto = AgentCrypto(password)
            empty_wallets = {'wallets': {}, 'version': '1.0.0'}
            encrypted = crypto.encrypt(empty_wallets)
            
            with open(self.wallets_file, 'wb') as f:
                f.write(encrypted)
            
            # Initialize address book
            with open(self.address_book_file, 'w') as f:
                json.dump({}, f)
            
            self.session.set_password(password)
            return True
        except Exception as e:
            print(f"Initialization failed: {e}")
            return False
    
    def unlock(self, password: str) -> bool:
        """Unlock wallet system with password."""
        try:
            if not self.wallets_file.exists():
                return False
            
            with open(self.wallets_file, 'rb') as f:
                encrypted_data = f.read()
            
            crypto = AgentCrypto(password)
            if not crypto.verify_password(encrypted_data):
                return False
            
            self.session.set_password(password)
            return True
        except Exception as e:
            print(f"Unlock failed: {e}")
            return False
    
    def _get_crypto(self) -> Optional[AgentCrypto]:
        """Get crypto instance if session is active."""
        password = self.session.get_password()
        if password:
            return AgentCrypto(password)
        return None
    
    def _load_wallets(self) -> Dict[str, Wallet]:
        """Load wallets from encrypted file."""
        if self._wallets_cache:
            return self._wallets_cache
        
        crypto = self._get_crypto()
        if not crypto:
            raise Exception("Wallet system locked. Please unlock first.")
        
        with open(self.wallets_file, 'rb') as f:
            encrypted_data = f.read()
        
        data = crypto.decrypt(encrypted_data)
        wallets_data = data.get('wallets', {})
        
        self._wallets_cache = {}
        for name, wallet_data in wallets_data.items():
            self._wallets_cache[name] = Wallet(**wallet_data)
        
        return self._wallets_cache
    
    def _save_wallets(self, wallets: Dict[str, Wallet]):
        """Save wallets to encrypted file."""
        crypto = self._get_crypto()
        if not crypto:
            raise Exception("Wallet system locked. Please unlock first.")
        
        wallets_data = {
            'wallets': {name: asdict(wallet) for name, wallet in wallets.items()},
            'version': '1.0.0'
        }
        
        encrypted = crypto.encrypt(wallets_data)
        with open(self.wallets_file, 'wb') as f:
            f.write(encrypted)
        
        self._wallets_cache = wallets
    
    def create_wallet(self, name: str, network: str = 'testnet') -> Wallet:
        """Create a new wallet."""
        if not self.session.is_active():
            raise Exception("Wallet system locked. Please unlock first.")
        
        wallets = self._load_wallets()
        
        if name in wallets:
            raise Exception(f"Wallet '{name}' already exists")
        
        # Generate new wallet
        # Note: This would use HoosatCrypto in production
        # For now, placeholder implementation
        import secrets
        private_key = secrets.token_hex(32)
        address = f"hoosat:{private_key[:20]}..."  # Simplified
        
        wallet = Wallet(
            name=name,
            address=address,
            private_key=private_key,
            network=network
        )
        
        wallets[name] = wallet
        self._save_wallets(wallets)
        
        return wallet
    
    def import_wallet(self, name: str, private_key: str, network: str = 'testnet') -> Wallet:
        """Import existing wallet."""
        if not self.session.is_active():
            raise Exception("Wallet system locked. Please unlock first.")
        
        wallets = self._load_wallets()
        
        if name in wallets:
            raise Exception(f"Wallet '{name}' already exists")
        
        # Derive address from private key
        # Note: Would use actual HoosatCrypto in production
        address = f"hoosat:{private_key[:20]}..."
        
        wallet = Wallet(
            name=name,
            address=address,
            private_key=private_key,
            network=network
        )
        
        wallets[name] = wallet
        self._save_wallets(wallets)
        
        return wallet
    
    def get_wallet(self, name: str) -> Optional[Wallet]:
        """Get wallet by name."""
        wallets = self._load_wallets()
        return wallets.get(name)
    
    def list_wallets(self) -> List[str]:
        """List all wallet names."""
        wallets = self._load_wallets()
        return list(wallets.keys())
    
    def get_wallet_info(self, name: str) -> Optional[Dict]:
        """Get wallet info (without private key)."""
        wallet = self.get_wallet(name)
        if not wallet:
            return None
        
        return {
            'name': wallet.name,
            'address': wallet.address,
            'network': wallet.network,
            'created_at': wallet.created_at
        }
    
    def delete_wallet(self, name: str) -> bool:
        """Delete a wallet."""
        wallets = self._load_wallets()
        
        if name not in wallets:
            return False
        
        del wallets[name]
        self._save_wallets(wallets)
        return True
    
    def export_wallet(self, name: str) -> Optional[Dict]:
        """Export wallet with private key."""
        wallet = self.get_wallet(name)
        if not wallet:
            return None
        
        return asdict(wallet)
    
    # Address Book Methods
    def _load_address_book(self) -> Dict[str, AddressEntry]:
        """Load address book."""
        if self._address_book_cache:
            return self._address_book_cache
        
        if not self.address_book_file.exists():
            return {}
        
        with open(self.address_book_file, 'r') as f:
            data = json.load(f)
        
        self._address_book_cache = {}
        for label, entry_data in data.items():
            self._address_book_cache[label] = AddressEntry(**entry_data)
        
        return self._address_book_cache
    
    def _save_address_book(self, address_book: Dict[str, AddressEntry]):
        """Save address book."""
        data = {label: asdict(entry) for label, entry in address_book.items()}
        with open(self.address_book_file, 'w') as f:
            json.dump(data, f, indent=2)
        
        self._address_book_cache = address_book
    
    def add_address(self, label: str, address: str, network: str = 'mainnet'):
        """Add address to address book."""
        address_book = self._load_address_book()
        
        entry = AddressEntry(
            label=label,
            address=address,
            network=network
        )
        
        address_book[label] = entry
        self._save_address_book(address_book)
    
    def get_address(self, label: str) -> Optional[str]:
        """Get address by label."""
        address_book = self._load_address_book()
        entry = address_book.get(label)
        return entry.address if entry else None
    
    def list_addresses(self) -> List[Dict]:
        """List all saved addresses."""
        address_book = self._load_address_book()
        return [asdict(entry) for entry in address_book.values()]
    
    def remove_address(self, label: str) -> bool:
        """Remove address from book."""
        address_book = self._load_address_book()
        
        if label not in address_book:
            return False
        
        del address_book[label]
        self._save_address_book(address_book)
        return True
    
    def resolve_address(self, identifier: str) -> Optional[str]:
        """Resolve identifier (label or address) to address."""
        # Check if it's a label
        address = self.get_address(identifier)
        if address:
            return address
        
        # Check if it's a wallet name
        wallet = self.get_wallet(identifier)
        if wallet:
            return wallet.address
        
        # Assume it's an address
        if identifier.startswith('hoosat:') or identifier.startswith('hoosattest:'):
            return identifier
        
        return None
    
    # Configuration Methods
    def set_auto_approve(self, wallet_name: str, max_amount: str, enabled: bool = True):
        """Configure auto-approve for a wallet."""
        self.config['autoApprove']['wallets'][wallet_name] = {
            'enabled': enabled,
            'maxAmount': max_amount
        }
        self._save_config()
    
    def get_auto_approve(self, wallet_name: str) -> Optional[Dict]:
        """Get auto-approve settings for wallet."""
        return self.config['autoApprove']['wallets'].get(wallet_name)
    
    def should_auto_approve(self, wallet_name: str, amount: str) -> bool:
        """Check if transaction should be auto-approved."""
        if not self.config['autoApprove']['enabled']:
            return False
        
        settings = self.get_auto_approve(wallet_name)
        if not settings or not settings['enabled']:
            return False
        
        return int(amount) <= int(settings['maxAmount'])
    
    def set_dry_run(self, enabled: bool):
        """Enable/disable dry run mode."""
        self.config['features']['dryRun'] = enabled
        self._save_config()
    
    def is_dry_run(self) -> bool:
        """Check if dry run mode is enabled."""
        return self.config['features']['dryRun']
    
    def set_confirm_transactions(self, enabled: bool):
        """Enable/disable transaction confirmation."""
        self.config['features']['confirmTransactions'] = enabled
        self._save_config()
    
    def should_confirm(self) -> bool:
        """Check if transactions should be confirmed."""
        return self.config['features']['confirmTransactions']
    
    def get_default_network(self) -> str:
        """Get default network."""
        return self.config['network']['default']
    
    def set_default_network(self, network: str):
        """Set default network."""
        self.config['network']['default'] = network
        self._save_config()
    
    def log_transaction(self, wallet_name: str, tx_id: str, recipient: str, amount: str):
        """Log a transaction."""
        if not self.config['features']['logTransactions']:
            return
        
        log_entry = {
            'timestamp': time.time(),
            'wallet': wallet_name,
            'tx_id': tx_id,
            'recipient': recipient,
            'amount': amount
        }
        
        with open(self.transaction_log, 'a') as f:
            f.write(json.dumps(log_entry) + '\n')
    
    def lock(self):
        """Lock wallet system."""
        self.session.clear()
        self._wallets_cache = {}
        self._address_book_cache = {}


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Hoosat Agent Wallet Manager')
    parser.add_argument('--password', '-p', help='Master password', default=None)
    parser.add_argument('--wallet-dir', '-d', help='Wallet directory', default=None)
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize wallet system')
    
    # Create wallet command
    create_parser = subparsers.add_parser('create', help='Create a new wallet')
    create_parser.add_argument('name', help='Wallet name')
    create_parser.add_argument('--network', '-n', default='mainnet', choices=['mainnet', 'testnet'])
    
    # List wallets command
    list_parser = subparsers.add_parser('list', help='List all wallets')
    
    # Get wallet info command
    info_parser = subparsers.add_parser('info', help='Get wallet info')
    info_parser.add_argument('name', help='Wallet name')
    
    # Export wallet command
    export_parser = subparsers.add_parser('export', help='Export wallet (shows private key)')
    export_parser.add_argument('name', help='Wallet name')
    
    # Delete wallet command
    delete_parser = subparsers.add_parser('delete', help='Delete a wallet')
    delete_parser.add_argument('name', help='Wallet name')
    
    # Add address command
    addaddr_parser = subparsers.add_parser('add-address', help='Add address to address book')
    addaddr_parser.add_argument('label', help='Address label')
    addaddr_parser.add_argument('address', help='Hoosat address')
    
    # List addresses command
    listaddr_parser = subparsers.add_parser('list-addresses', help='List saved addresses')
    
    # Balance command (requires agent-transact.py)
    balance_parser = subparsers.add_parser('balance', help='Check wallet balance (requires agent-transact)')
    balance_parser.add_argument('name', help='Wallet name')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Initialize manager
    manager = AgentWalletManager(wallet_dir=args.wallet_dir)
    
    # Handle init command
    if args.command == 'init':
        if manager.is_initialized():
            print("Wallet system already initialized")
            return
        
        password = args.password or input("Set master password: ")
        if manager.initialize(password):
            print("✓ Wallet system initialized")
        else:
            print("✗ Failed to initialize")
        return
    
    # Check if initialized
    if not manager.is_initialized():
        print("Wallet system not initialized. Run: init")
        return
    
    # Unlock
    password = args.password or input("Enter password: ")
    if not manager.unlock(password):
        print("✗ Invalid password")
        return
    
    # Execute command
    try:
        if args.command == 'create':
            wallet = manager.create_wallet(args.name, args.network)
            print(f"✓ Created wallet: {wallet.name}")
            print(f"  Address: {wallet.address}")
            print(f"  Network: {wallet.network}")
            print(f"\n⚠️  IMPORTANT: Backup your private key!")
            print(f"  Run: export {wallet.name}")
            
        elif args.command == 'list':
            wallets = manager.list_wallets()
            if not wallets:
                print("No wallets found")
            else:
                print(f"Wallets ({len(wallets)}):")
                for name in wallets:
                    info = manager.get_wallet_info(name)
                    print(f"  - {name}: {info['address']} ({info['network']})")
                    
        elif args.command == 'info':
            info = manager.get_wallet_info(args.name)
            if info:
                print(f"Wallet: {info['name']}")
                print(f"Address: {info['address']}")
                print(f"Network: {info['network']}")
                print(f"Created: {info['created_at']}")
            else:
                print(f"Wallet '{args.name}' not found")
                
        elif args.command == 'export':
            wallet = manager.get_wallet(args.name)
            if wallet:
                print(f"⚠️  SECURITY WARNING - Private Key for {args.name}:")
                print(f"  Address: {wallet.address}")
                print(f"  Private Key (hex): {wallet.private_key}")
                print("\n  Save this securely and NEVER share it!")
            else:
                print(f"Wallet '{args.name}' not found")
                
        elif args.command == 'delete':
            if manager.delete_wallet(args.name):
                print(f"✓ Deleted wallet: {args.name}")
            else:
                print(f"Wallet '{args.name}' not found")
                
        elif args.command == 'add-address':
            manager.add_address(args.label, args.address)
            print(f"✓ Added address: {args.label} -> {args.address}")
            
        elif args.command == 'list-addresses':
            addresses = manager.list_addresses()
            if not addresses:
                print("No saved addresses")
            else:
                print(f"Saved addresses ({len(addresses)}):")
                for entry in addresses:
                    print(f"  - {entry['label']}: {entry['address']}")
                    
        elif args.command == 'balance':
            wallet = manager.get_wallet(args.name)
            if not wallet:
                print(f"Wallet '{args.name}' not found")
                return
            print(f"To check balance, use agent-transact.py:")
            print(f"  python3 agent-transact.py balance {args.name}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == '__main__':
    main()
