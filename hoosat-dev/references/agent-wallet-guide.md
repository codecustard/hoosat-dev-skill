# Hoosat Agent Wallet Guide

Complete guide for using the Hoosat agent wallet system for autonomous blockchain interactions.

## Overview

The agent wallet system allows AI agents to:
- Create and manage encrypted wallets
- Query balances and UTXOs
- Execute transactions (with confirmation or auto-approve)
- Maintain an address book
- Consolidate UTXOs

## Installation

### Requirements
```bash
pip install cryptography requests
```

### Initialize Wallet System

```bash
python hoosat-dev/scripts/agent-wallet.py
```

Or via the skill:
```
"Initialize hoosat wallet system"
```

## Quick Start

### 1. Set Master Password
```
"Set wallet password to my_secure_password_123"
```

The password is stored in environment variable `HOOSAT_AGENT_PASSWORD` for the session.

### 2. Create a Wallet
```
"Create wallet named mining on testnet"
```

### 3. Check Balance
```
"Check balance of mining wallet"
```

### 4. Transfer Funds
```
"Transfer 5 HTN from mining to hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"
```

## Wallet Commands

### Create Wallet
```
"Create wallet [name] on [network]"

Example:
"Create wallet trading on mainnet"
"Create wallet mining on testnet"
```

### Import Wallet
```
"Import wallet [name] with private key [key] on [network]"

Example:
"Import wallet old_wallet with private key Kxabc123... on mainnet"
```

### List Wallets
```
"List all wallets"
"Show my wallets"
```

### Get Wallet Info
```
"Show info for [name] wallet"
"Get address of [name] wallet"
```

### Delete Wallet
```
"Delete wallet [name]"
```

### Export Wallet
```
"Export wallet [name]"
"Show private key for [name] wallet"
```

## Transaction Commands

### Transfer
```
"Transfer [amount] HTN from [wallet] to [address]"
"Send [amount] from [wallet] to [address]"

Examples:
"Transfer 10 HTN from mining to hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"
"Send 5 HTN from trading to exchange"
```

### Send All
```
"Send all funds from [wallet] to [address]"
"Sweep wallet [name] to [address]"

Example:
"Send all funds from mining to trading"
```

### Consolidate UTXOs
```
"Consolidate UTXOs in [wallet]"
"Compound UTXOs in [wallet]"

Example:
"Consolidate UTXOs in mining wallet"
```

## Address Book Commands

### Add Address
```
"Save address [label] as [address]"
"Add [label] to address book: [address]"

Examples:
"Save address exchange as hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"
"Add mining_pool to address book: hoosat:qqkqkzjvr7zwxxmjxjkmxx"
```

### List Addresses
```
"Show address book"
"List saved addresses"
```

### Remove Address
```
"Remove address [label] from book"
"Delete [label] from address book"
```

## Balance & Queries

### Check Balance
```
"Check balance of [wallet]"
"How much HTN in [wallet]?"
"What's the balance of [wallet]?"
```

### List UTXOs
```
"List UTXOs in [wallet]"
"Show spendable outputs for [wallet]"
```

### Transaction History
```
"Show transaction history"
"List recent transactions"
```

## Configuration Commands

### Set Auto-Approve
```
"Enable auto-approve for [wallet] up to [amount] HTN"
"Allow [wallet] to auto-send under [amount] HTN"

Examples:
"Enable auto-approve for mining up to 10 HTN"
"Allow trading wallet to auto-send under 50 HTN"
```

### Disable Auto-Approve
```
"Disable auto-approve for [wallet]"
"Require confirmation for all [wallet] transactions"
```

### Set Dry-Run Mode
```
"Enable dry-run mode"    # Test without broadcasting
"Disable dry-run mode"   # Actually send transactions
```

### Change Network
```
"Switch to mainnet"
"Use testnet"
"Set default network to [mainnet/testnet]"
```

### Lock Wallet
```
"Lock wallet system"
"Clear wallet session"
```

## Security Features

### Encryption
- All wallets stored encrypted with AES-256-CBC
- Master password required to unlock
- PBKDF2 key derivation (100,000 iterations)
- Automatic session timeout (1 hour default)

### Auto-Approve
- Configure per-wallet limits
- Transactions under limit execute automatically
- Transactions over limit require confirmation
- Default: Disabled (all transactions require confirmation)

### Dry-Run Mode
- Test transactions without broadcasting
- Shows what would happen
- Calculates fees
- Safe for testing

## Configuration File

Located at: `~/.hoosat-wallets/config.json`

```json
{
  "version": "1.0.0",
  "security": {
    "requirePasswordEvery": "session",
    "autoLockAfter": 3600,
    "sessionTimeout": 3600
  },
  "autoApprove": {
    "enabled": false,
    "defaultMaxAmount": "100000000",
    "wallets": {
      "mining": {
        "enabled": true,
        "maxAmount": "5000000000"
      }
    }
  },
  "network": {
    "default": "testnet",
    "apiEndpoints": {
      "mainnet": "https://proxy.hoosat.net/api/v1",
      "testnet": "https://proxy.hoosat.net/api/v1"
    }
  },
  "features": {
    "dryRun": true,
    "confirmTransactions": true,
    "logTransactions": true
  }
}
```

## File Structure

```
~/.hoosat-wallets/
├── config.json           # Agent configuration
├── wallets.enc          # Encrypted wallets
├── address-book.json    # Saved addresses
└── transactions.log     # Transaction history
```

## Examples

### Mining Setup
```
"Create wallet mining on mainnet"
"What's the address of mining wallet?"
"Save address mining_pool as hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"
"Enable auto-approve for mining up to 1 HTN"
"Transfer 0.5 HTN from mining to mining_pool"
```

### Trading Workflow
```
"Create wallet trading on mainnet"
"Create wallet savings on mainnet"
"Check balance of trading"
"Send 10 HTN from trading to exchange"
"Consolidate UTXOs in trading"
"Send all from trading to savings"
```

### Address Book Management
```
"Save address exchange1 as hoosat:abc123..."
"Save address exchange2 as hoosat:def456..."
"Save address friend as hoosat:ghi789..."
"List saved addresses"
"Send 5 HTN to friend"
```

## Troubleshooting

### "Wallet system locked"
- Enter password: "Unlock wallet with password [your_password]"

### "Insufficient balance"
- Check balance first: "Check balance of [wallet]"
- Verify you're on correct network

### "Invalid address"
- Ensure address starts with `hoosat:` or `hoosattest:`
- Check for typos

### "Transaction failed"
- Check transaction log: `~/.hoosat-wallets/transactions.log`
- Verify network connectivity
- Check if API is available

### Lost Password
- No recovery possible (encryption is secure)
- Always backup private keys when creating wallets
- Store password securely

## Best Practices

1. **Start with testnet** - Practice before using real funds
2. **Backup private keys** - Export and store securely
3. **Use auto-approve carefully** - Set reasonable limits
4. **Enable dry-run first** - Test before real transactions
5. **Consolidate regularly** - Keep UTXO count low for efficiency
6. **Lock when done** - Clear session when finished

## Safety Warnings

⚠️ **Never share private keys**
⚠️ **Always verify addresses before sending**
⚠️ **Test on testnet first**
⚠️ **Keep master password secure**
⚠️ **Backup wallet files regularly**
