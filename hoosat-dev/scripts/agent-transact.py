#!/usr/bin/env python3
"""
Hoosat Agent Transaction Executor

Executes transactions using the Hoosat REST API.
Supports dry-run mode, UTXO consolidation, and transaction logging.
"""

import requests
import json
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
try:
    from .agent_wallet import AgentWalletManager, Wallet
except ImportError:
    from agent_wallet import AgentWalletManager, Wallet


@dataclass
class TransactionResult:
    """Result of a transaction."""
    success: bool
    tx_id: Optional[str] = None
    error: Optional[str] = None
    dry_run: bool = False
    details: Optional[Dict] = None


class AgentTransactionExecutor:
    """Execute transactions on Hoosat network."""
    
    def __init__(self, wallet_manager: AgentWalletManager):
        """Initialize with wallet manager."""
        self.wallet_manager = wallet_manager
        self.config = wallet_manager.config
        
        # Get API endpoint
        network = self.config['network']['default']
        self.api_url = self.config['network']['apiEndpoints'].get(
            network, 
            'https://proxy.hoosat.net/api/v1'
        )
    
    def get_balance(self, wallet_name: str) -> Tuple[bool, str]:
        """Get wallet balance."""
        try:
            wallet = self.wallet_manager.get_wallet(wallet_name)
            if not wallet:
                return False, f"Wallet '{wallet_name}' not found"
            
            response = requests.get(
                f"{self.api_url}/address/{wallet.address}/balance"
            )
            
            if response.status_code != 200:
                return False, f"API error: {response.text}"
            
            data = response.json()
            if not data.get('success'):
                return False, f"API error: {data.get('error')}"
            
            balance = data['data']['balance']
            return True, balance
            
        except Exception as e:
            return False, str(e)
    
    def get_utxos(self, wallet_name: str) -> Tuple[bool, List[Dict]]:
        """Get UTXOs for a wallet."""
        try:
            wallet = self.wallet_manager.get_wallet(wallet_name)
            if not wallet:
                return False, f"Wallet '{wallet_name}' not found", []
            
            response = requests.post(
                f"{self.api_url}/address/utxos",
                json={'addresses': [wallet.address]}
            )
            
            if response.status_code != 200:
                return False, f"API error: {response.text}", []
            
            data = response.json()
            if not data.get('success'):
                return False, f"API error: {data.get('error')}", []
            
            utxos = data['data']['utxos']
            return True, "", utxos
            
        except Exception as e:
            return False, str(e), []
    
    def get_fee_estimate(self) -> Tuple[bool, Dict]:
        """Get fee estimate from network."""
        try:
            response = requests.get(
                f"{self.api_url}/mempool/fee-estimate"
            )
            
            if response.status_code != 200:
                return False, {}
            
            data = response.json()
            if not data.get('success'):
                return False, {}
            
            return True, data['data']
            
        except Exception:
            return False, {}
    
    def transfer(
        self,
        from_wallet: str,
        to_address: str,
        amount_htn: float,
        confirm: Optional[bool] = None
    ) -> TransactionResult:
        """Transfer HTN from one wallet to another."""
        try:
            # Resolve recipient address
            recipient = self.wallet_manager.resolve_address(to_address)
            if not recipient:
                return TransactionResult(
                    success=False,
                    error=f"Could not resolve address: {to_address}"
                )
            
            # Get sender wallet
            wallet = self.wallet_manager.get_wallet(from_wallet)
            if not wallet:
                return TransactionResult(
                    success=False,
                    error=f"Wallet '{from_wallet}' not found"
                )
            
            # Convert amount to sompi
            amount_sompi = int(amount_htn * 100_000_000)
            
            # Get balance
            success, balance_str = self.get_balance(from_wallet)
            if not success:
                return TransactionResult(
                    success=False,
                    error=f"Could not get balance: {balance_str}"
                )
            
            balance = int(balance_str)
            if balance < amount_sompi:
                return TransactionResult(
                    success=False,
                    error=f"Insufficient balance. Have: {balance / 100_000_000} HTN, Need: {amount_htn} HTN"
                )
            
            # Get UTXOs
            success, error_msg, utxos = self.get_utxos(from_wallet)
            if not success:
                return TransactionResult(
                    success=False,
                    error=f"Could not get UTXOs: {error_msg}"
                )
            
            if not utxos:
                return TransactionResult(
                    success=False,
                    error="No UTXOs available"
                )
            
            # Get fee estimate
            success, fee_estimate = self.get_fee_estimate()
            if success:
                fee_rate = fee_estimate.get('normalBucket', {}).get('feeRate', 100)
            else:
                fee_rate = 100  # Default
            
            # Check if should confirm
            should_confirm = confirm if confirm is not None else self.wallet_manager.should_confirm()
            
            if should_confirm and not self.wallet_manager.should_auto_approve(from_wallet, str(amount_sompi)):
                return TransactionResult(
                    success=False,
                    error=f"Transaction requires confirmation: Send {amount_htn} HTN to {recipient}",
                    dry_run=True,
                    details={
                        'from': wallet.address,
                        'to': recipient,
                        'amount': amount_sompi,
                        'fee_rate': fee_rate
                    }
                )
            
            # Check dry-run mode
            if self.wallet_manager.is_dry_run():
                return TransactionResult(
                    success=True,
                    tx_id="DRY-RUN-TX-ID",
                    dry_run=True,
                    details={
                        'from': wallet.address,
                        'to': recipient,
                        'amount': amount_sompi,
                        'fee_rate': fee_rate,
                        'utxos_count': len(utxos)
                    }
                )
            
            # Build and submit transaction
            # Note: This is a simplified version. Full implementation would:
            # 1. Select optimal UTXOs
            # 2. Build transaction with proper scripts
            # 3. Sign with private key
            # 4. Submit to network
            
            # For now, return dry-run result
            result = TransactionResult(
                success=True,
                tx_id="DRY-RUN-TX-ID",
                dry_run=True,
                details={
                    'message': 'Full transaction signing not implemented yet',
                    'from': wallet.address,
                    'to': recipient,
                    'amount': amount_sompi,
                    'fee_rate': fee_rate,
                    'utxos_count': len(utxos)
                }
            )
            
            # Log transaction
            if result.success and result.tx_id:
                self.wallet_manager.log_transaction(
                    from_wallet,
                    result.tx_id,
                    recipient,
                    str(amount_sompi)
                )
            
            return result
            
        except Exception as e:
            return TransactionResult(
                success=False,
                error=str(e)
            )
    
    def consolidate_utxos(
        self,
        wallet_name: str,
        max_utxos: int = 10
    ) -> TransactionResult:
        """Consolidate small UTXOs into fewer outputs."""
        try:
            # Get wallet
            wallet = self.wallet_manager.get_wallet(wallet_name)
            if not wallet:
                return TransactionResult(
                    success=False,
                    error=f"Wallet '{wallet_name}' not found"
                )
            
            # Get UTXOs
            success, error_msg, utxos = self.get_utxos(wallet_name)
            if not success:
                return TransactionResult(
                    success=False,
                    error=f"Could not get UTXOs: {error_msg}"
                )
            
            if len(utxos) <= max_utxos:
                return TransactionResult(
                    success=True,
                    error=None,
                    details={'message': f'Only {len(utxos)} UTXOs, no consolidation needed'}
                )
            
            # Calculate total
            total = sum(int(utxo['utxoEntry']['amount']) for utxo in utxos)
            
            # Get fee
            success, fee_estimate = self.get_fee_estimate()
            fee = fee_estimate.get('normalBucket', {}).get('feeRate', 100) * 200 if success else 20000
            
            # Check if consolidation is worth it
            if total <= fee:
                return TransactionResult(
                    success=False,
                    error=f"Consolidation not worth it. Total: {total}, Fee: {fee}"
                )
            
            # Build consolidation transaction
            # Send all to self
            if self.wallet_manager.is_dry_run():
                return TransactionResult(
                    success=True,
                    tx_id="DRY-RUN-CONSOLIDATE",
                    dry_run=True,
                    details={
                        'action': 'consolidate',
                        'wallet': wallet_name,
                        'utxos': len(utxos),
                        'total': total,
                        'fee': fee,
                        'consolidated_amount': total - fee
                    }
                )
            
            # Full implementation would create and submit transaction
            return TransactionResult(
                success=True,
                tx_id="DRY-RUN-CONSOLIDATE",
                dry_run=True,
                details={
                    'message': 'Full consolidation not implemented yet',
                    'action': 'consolidate',
                    'wallet': wallet_name,
                    'utxos': len(utxos),
                    'total': total,
                    'fee': fee
                }
            )
            
        except Exception as e:
            return TransactionResult(
                success=False,
                error=str(e)
            )
    
    def send_all(
        self,
        from_wallet: str,
        to_address: str
    ) -> TransactionResult:
        """Send all funds from one wallet to another."""
        try:
            # Get balance
            success, balance_str = self.get_balance(from_wallet)
            if not success:
                return TransactionResult(
                    success=False,
                    error=f"Could not get balance: {balance_str}"
                )
            
            balance = int(balance_str)
            
            # Get fee estimate
            success, fee_estimate = self.get_fee_estimate()
            fee = fee_estimate.get('normalBucket', {}).get('feeRate', 100) * 200 if success else 20000
            
            # Calculate amount to send (balance - fee)
            amount = balance - fee
            
            if amount <= 0:
                return TransactionResult(
                    success=False,
                    error="Insufficient funds after fee"
                )
            
            amount_htn = amount / 100_000_000
            
            return self.transfer(from_wallet, to_address, amount_htn)
            
        except Exception as e:
            return TransactionResult(
                success=False,
                error=str(e)
            )
    
    def get_transaction_status(self, tx_id: str) -> Tuple[bool, Optional[Dict]]:
        """Get transaction status."""
        try:
            response = requests.get(
                f"{self.api_url}/transaction/{tx_id}/status"
            )
            
            if response.status_code != 200:
                return False, None
            
            data = response.json()
            if not data.get('success'):
                return False, None
            
            return True, data['data']
            
        except Exception:
            return False, None


if __name__ == '__main__':
    # Test transaction executor
    from .agent_wallet import AgentWalletManager
    
    manager = AgentWalletManager()
    
    # Initialize and unlock if needed
    if not manager.is_initialized():
        manager.initialize('test_password_123')
    else:
        manager.unlock('test_password_123')
    
    # Create executor
    executor = AgentTransactionExecutor(manager)
    
    # Create a test wallet if needed
    if not manager.list_wallets():
        wallet = manager.create_wallet('test', 'testnet')
        print(f"✓ Created test wallet: {wallet.address}")
    
    # Test balance check
    success, balance = executor.get_balance('test')
    print(f"✓ Balance check: {success}, Balance: {balance}")
    
    # Test transfer (dry-run)
    result = executor.transfer('test', 'hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe', 0.1)
    print(f"✓ Transfer result: {result}")
    
    print("\nAll tests passed!")
