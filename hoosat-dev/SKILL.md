---
name: hoosat-dev
description: "Comprehensive Hoosat blockchain development toolkit for building transactions, integrating wallets, creating dApps, and interacting with the Hoosat network (a Kaspa fork using Blake3 and Hoohash). Use when working with Hoosat blockchain development including: (1) Building and broadcasting HTN transactions, (2) Generating addresses with hoosat: prefix, (3) Creating dApps using hoosat-sdk or hoosat-sdk-web, (4) Integrating Hoosat wallets, (5) Using Hoosat SDKs (Node.js hoosat-sdk, Browser hoosat-sdk-web, Motoko hoosat-mo for IC), (6) Using the Hoosat REST API at proxy.hoosat.net, (7) Working with HRC20 tokens. Supports JavaScript/TypeScript (Node.js and Browser), Go, and Motoko (Internet Computer) development."
---

# Hoosat Development

## Overview

This skill provides comprehensive support for Hoosat blockchain development. Hoosat is a Kaspa fork that uses BLAKE3 and Hoohash consensus algorithms with HTN as its native token.

**Key Characteristics:**
- **Ticker**: HTN
- **Address Prefix**: `hoosat:` (mainnet), `hoosattest:` (testnet)
- **Consensus**: BLAKE3 and Hoohash (not kHash like Kaspa)
- **SDKs**: hoosat-sdk (Node.js), hoosat-sdk-web (Browser), hoosat-mo (Motoko/IC)
- **API**: https://proxy.hoosat.net/api/v1 (no auth required)
- **Token Standard**: HRC20 (KRC20 equivalent, in progress)

**GitHub Repositories:**
- https://github.com/hoosatnetwork
- https://github.com/Namp88

## Quick Start

### Choose Your SDK

| Environment | Package | Install |
|------------|---------|---------|
| **Node.js** | `hoosat-sdk` | `npm install hoosat-sdk` |
| **Browser** | `hoosat-sdk-web` | `npm install hoosat-sdk-web` |
| **Motoko (IC)** | `hoosat-mo` | `mops install hoosat-mo` |

### Generate a Hoosat Address

**Node.js (hoosat-sdk):**
```javascript
import { HoosatCrypto } from 'hoosat-sdk';

const wallet = HoosatCrypto.generateKeyPair('mainnet');
console.log('Address:', wallet.address);
console.log('Private Key:', wallet.privateKey.toString('hex'));
```

**Browser (hoosat-sdk-web):**
```javascript
import { HoosatCrypto } from 'hoosat-sdk-web';

const wallet = HoosatCrypto.generateKeyPair('mainnet');
```

**Python:**
```python
python scripts/generate-address.py --network mainnet
```

### Check Balance

**Node.js:**
```javascript
import { HoosatClient, HoosatUtils } from 'hoosat-sdk';

const client = new HoosatClient({
  host: '54.38.176.95',
  port: 42420
});

const result = await client.getBalance('hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe');
if (result.ok) {
  const htn = HoosatUtils.sompiToAmount(result.result.balance);
  console.log(`Balance: ${htn} HTN`);
}
```

**Browser:**
```javascript
import { HoosatWebClient } from 'hoosat-sdk-web';

const client = new HoosatWebClient({
  baseUrl: 'https://proxy.hoosat.net/api/v1'
});

const balance = await client.getBalance(address);
```

**REST API:**
```bash
curl https://proxy.hoosat.net/api/v1/address/hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe/balance
```

### Send a Transaction

**Node.js:**
```javascript
import { HoosatClient, HoosatCrypto, HoosatTxBuilder, HoosatUtils } from 'hoosat-sdk';

const client = new HoosatClient({ host: '54.38.176.95', port: 42420 });
const wallet = HoosatCrypto.importKeyPair(process.env.WALLET_PRIVATE_KEY);

// Get UTXOs
const utxosResult = await client.getUtxosByAddresses([wallet.address]);
const utxos = utxosResult.result.utxos;

// Calculate minimum fee
const minFee = await client.calculateMinFee(wallet.address);

// Build transaction
const builder = new HoosatTxBuilder();
for (const utxo of utxos) {
  builder.addInput(utxo, wallet.privateKey);
}
builder
  .addOutput(recipientAddress, HoosatUtils.amountToSompi('1.0'))
  .setFee(minFee)
  .addChangeOutput(wallet.address);

const signedTx = builder.sign();

// Submit
const result = await client.submitTransaction(signedTx);
if (result.ok) {
  console.log('TX ID:', result.result.transactionId);
}
```

### Sign a Message

**Node.js:**
```javascript
import { HoosatSigner } from 'hoosat-sdk';

const signature = HoosatSigner.signMessage(message, wallet.privateKey);
const isValid = HoosatSigner.verifyMessage(message, signature, wallet.publicKey);
```

### Motoko (Internet Computer)

```motoko
import Wallet "mo:hoosat-mo/wallet";
import Address "mo:hoosat-mo/address";

let wallet = Wallet.createMainnetWallet("key", ?"hoosat");
let result = await wallet.sendTransaction(from, to, amount, null, null);
```

## SDK Modules Overview

### HoosatClient (Node.js)
Main client for gRPC connection to Hoosat nodes.

```javascript
const client = new HoosatClient({
  host: '54.38.176.95',
  port: 42420
});
```

**Key Methods:**
- `getBalance(address)` - Get address balance
- `getUtxosByAddresses(addresses)` - Get UTXOs
- `submitTransaction(tx)` - Submit signed transaction
- `calculateMinFee(address)` - Calculate minimum fee
- `events.subscribeToUtxoChanges(addresses)` - Real-time UTXO monitoring

### HoosatCrypto (Node.js & Browser)
Cryptographic operations with BLAKE3 hashing.

**Key Methods:**
- `generateKeyPair(network)` - Generate new wallet
- `importKeyPair(privateKey, network)` - Import existing wallet
- `signTransactionInput(tx, index, privateKey, utxo)` - Sign transaction input
- `blake3Hash(data)` - BLAKE3 hashing

### HoosatTxBuilder (Node.js & Browser)
Fluent transaction builder.

```javascript
const builder = new HoosatTxBuilder();
builder
  .addInput(utxo, privateKey)
  .addOutput(recipientAddress, amount)
  .setFee(fee)
  .addChangeOutput(changeAddress);
  
const signedTx = builder.sign();
```

### HoosatUtils (Node.js & Browser)
Utility functions for validation and conversion.

- `amountToSompi(htn)` - Convert HTN to sompi (1 HTN = 100M sompi)
- `sompiToAmount(sompi)` - Convert sompi to HTN
- `isValidAddress(address)` - Validate address
- `getAddressNetwork(address)` - Get network from address

### HoosatEventManager (Node.js)
Real-time event streaming.

```javascript
await client.events.subscribeToUtxoChanges([address]);
client.events.on(EventType.UtxoChange, (notification) => {
  console.log('Balance changed!');
});
```

### HoosatQR (Node.js & Browser)
QR code generation for payments.

```javascript
const qr = await HoosatQR.generatePaymentQR({
  address: merchantAddress,
  amount: HoosatUtils.amountToSompi('1.5'),
  label: 'My Store',
  message: 'Order #12345'
});
```

### HoosatSigner (Node.js & Browser)
Message signing for authentication.

```javascript
const signature = HoosatSigner.signMessage(message, privateKey);
const isValid = HoosatSigner.verifyMessage(message, signature, publicKey);
```

## Error Handling

All SDK methods use a consistent error handling pattern:

```typescript
interface BaseResult<T> {
  ok: boolean;
  result?: T;
  error?: string;
}

// Usage
const result = await client.getBalance(address);
if (result.ok) {
  console.log('Balance:', result.result.balance);
} else {
  console.error('Error:', result.error);
}
```

## Network Types

- **Mainnet**: Production network (prefix: `hoosat:`)
- **Testnet**: Testing network (prefix: `hoosattest:`)

## Address Formats

Hoosat uses Bech32 encoding:

- Mainnet: `hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe`
- Testnet: `hoosattest:qqkqkzjvr7zwxxmjxjkmxx`

## Unit Conversion

- 1 HTN = 100,000,000 sompi
- Dust threshold: 1,000 sompi minimum
- Use `HoosatUtils.amountToSompi()` and `HoosatUtils.sompiToAmount()` for conversions

## SDK References

For detailed SDK documentation:

- **Node.js SDK**: See [references/hoosat-sdk.md](references/hoosat-sdk.md)
- **Browser SDK**: See [references/hoosat-sdk-web.md](references/hoosat-sdk-web.md)
- **Motoko Package**: See [references/hoosat-mo.md](references/hoosat-mo.md)
- **REST API**: See [references/api-reference.md](references/api-reference.md)

## Integration Guides

### Wallet Integration

See [references/wallet-integration.md](references/wallet-integration.md) for:
- Wallet connection patterns
- Transaction signing flows
- Address management
- Network switching

### Node Operations

See [references/node-operations.md](references/node-operations.md) for:
- Docker deployment
- Binary installation
- Building from source
- RPC node setup

### dApp Development

When building a Hoosat dApp:

1. **Setup**: Use `hoosat-sdk-web` for browser compatibility
2. **Wallet Connection**: Implement wallet adapter using HoosatCrypto
3. **State Management**: Track balances, transactions, and UTXOs
4. **Transaction Building**: Use HoosatTxBuilder with UTXO selection
5. **Error Handling**: Handle BaseResult<T> pattern

Use the `dapp-template/` asset for a starter React/Next.js dApp.

### Block Explorer

To build a block explorer:

1. **Data Source**: Use Hoosat REST API or run your own node
2. **Indexing**: Index blocks, transactions, and addresses
3. **API Layer**: Build REST/GraphQL API using HoosatWebClient
4. **Frontend**: Display blocks, transactions, addresses

Use the `explorer-template/` asset for a starter block explorer.

## HRC20 Tokens

HRC20 is Hoosat's token standard (KRC20 equivalent). For token development:

See [references/hrc20-tokens.md](references/hrc20-tokens.md) for:
- Token contract structure
- Transfer and approval mechanisms
- Integration patterns

## Scripts and Utilities

The `scripts/` directory contains utility scripts:

- `generate-address.py`: Generate Hoosat addresses with BLAKE3
- `build-transaction.py`: Build and sign transactions

## Resources

### References

- **api-reference.md**: Hoosat REST API documentation (proxy.hoosat.net)
- **hoosat-sdk.md**: Node.js SDK documentation
- **hoosat-sdk-web.md**: Browser SDK documentation
- **hoosat-mo.md**: Motoko (Internet Computer) documentation
- **wallet-integration.md**: Wallet integration patterns
- **node-operations.md**: Node operations guide
- **hrc20-tokens.md**: HRC20 token standard

### Assets

- **dapp-template/**: React/Next.js dApp starter using hoosat-sdk-web
- **explorer-template/**: Block explorer starter

## Best Practices

1. **Always validate addresses** before using them (check `hoosat:` or `hoosattest:` prefix)
2. **Handle UTXO selection** carefully to avoid dust outputs (min 1000 sompi)
3. **Implement proper error handling** using BaseResult<T> pattern
4. **Test on testnet** before mainnet deployment
5. **Use fee estimation** via `client.calculateMinFee()` for proper fees
6. **Secure private keys** - never expose them in client-side code
7. **Use BLAKE3 hashing** for any custom cryptographic operations
8. **Convert amounts properly** using HoosatUtils (1 HTN = 100M sompi)

## Getting Help

- **Developer Hub**: https://hub.hoosat.net/
- **REST API Docs**: https://proxy.hoosat.net/docs
- **GitHub (Network)**: https://github.com/hoosatnetwork
- **GitHub (Developer)**: https://github.com/Namp88
- **GitHub (Organization)**: https://github.com/Hoosat-Oy
- **Discord**: https://discord.gg/mFBfNpNA
- **Twitter**: https://x.com/HoosatNetwork
- **Telegram**: https://t.me/HoosatNetwork
- **Official Website**: https://network.hoosat.fi
- **Motoko Package**: https://mops.one/hoosat-mo


