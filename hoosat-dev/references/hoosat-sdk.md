# Hoosat Node.js SDK (hoosat-sdk)

Complete reference for the Hoosat Node.js SDK using direct gRPC connections.

## Installation

```bash
npm install hoosat-sdk
# or
yarn add hoosat-sdk
```

## Quick Start

```typescript
import { HoosatClient, HoosatCrypto, HoosatUtils } from 'hoosat-sdk';

// Create client
const client = new HoosatClient({
  host: '54.38.176.95',
  port: 42420
});

// Generate wallet
const wallet = HoosatCrypto.generateKeyPair('mainnet');
console.log('Address:', wallet.address);

// Check balance
const result = await client.getBalance(wallet.address);
if (result.ok) {
  const htn = HoosatUtils.sompiToAmount(result.result.balance);
  console.log(`Balance: ${htn} HTN`);
}
```

## HoosatClient

Main client for connecting to Hoosat nodes via gRPC.

### Constructor

```typescript
const client = new HoosatClient({
  host: string;      // Node host IP or domain
  port: number;      // Node port (default: 42420)
});
```

### Connection Management

```typescript
// Connect to node (automatically called by most methods)
await client.connect();

// Check connection status
const isConnected = client.isConnected();

// Disconnect
await client.disconnect();
```

### Balance Operations

#### Get Balance

```typescript
const result = await client.getBalance(address: string);

// Response type: BaseResult<{ balance: string }>
if (result.ok) {
  console.log('Balance (sompi):', result.result.balance);
}
```

#### Get Balances by Addresses

```typescript
const result = await client.getBalancesByAddresses(addresses: string[]);

// Response type: BaseResult<{ entries: BalanceEntry[] }>
if (result.ok) {
  result.result.entries.forEach(entry => {
    console.log(`${entry.address}: ${entry.balance} sompi`);
  });
}
```

### UTXO Operations

#### Get UTXOs by Addresses

```typescript
const result = await client.getUtxosByAddresses(addresses: string[]);

// Response type: BaseResult<{ utxos: UtxoForSigning[] }>
if (result.ok) {
  result.result.utxos.forEach(utxo => {
    console.log('UTXO:', utxo.outpoint.transactionId, utxo.outpoint.index);
    console.log('Amount:', utxo.utxoEntry.amount);
  });
}
```

### Transaction Operations

#### Submit Transaction

```typescript
const result = await client.submitTransaction(transaction: Transaction);

// Response type: BaseResult<{ transactionId: string }>
if (result.ok) {
  console.log('Transaction ID:', result.result.transactionId);
}
```

#### Calculate Minimum Fee

```typescript
// Automatic fee calculation based on UTXOs
const result = await client.calculateMinFee(address: string, payloadSize?: number);

// Response type: BaseResult<{ fee: string }>
if (result.ok) {
  console.log('Minimum fee:', result.result.fee, 'sompi');
}
```

### Block Operations

```typescript
// Get block by hash
const blockResult = await client.getBlock({
  hash: string,
  includeTransactions?: boolean
});

// Get blocks
const blocksResult = await client.getBlocks({
  lowHash: string,
  includeBlocks?: boolean,
  includeTransactions?: boolean
});

// Get block DAG info
const dagInfoResult = await client.getBlockDagInfo();

// Get sink (tip)
const sinkResult = await client.getSink();

// Get sink blue score
const blueScoreResult = await client.getSinkBlueScore();
```

### Mempool Operations

```typescript
// Get mempool entries
const mempoolResult = await client.getMempoolEntries({
  includeOrphanPool?: boolean,
  filterTransactionPool?: boolean
});

// Get specific mempool entry
const entryResult = await client.getMempoolEntry({
  transactionId: string,
  includeOrphanPool?: boolean
});

// Get mempool entries by addresses
const addressMempoolResult = await client.getMempoolEntriesByAddresses({
  addresses: string[],
  includeOrphanPool?: boolean,
  filterTransactionPool?: boolean
});
```

### Network Operations

```typescript
// Get current network
const networkResult = await client.getCurrentNetwork();

// Get coin supply
const supplyResult = await client.getCoinSupply();

// Estimate network hashrate
const hashrateResult = await client.estimateNetworkHashesPerSecond({
  windowSize: number
});
```

## HoosatCrypto

Cryptographic operations for key management and transactions using BLAKE3 hashing.

### Key Generation

```typescript
import { HoosatCrypto } from 'hoosat-sdk';

// Generate new key pair
const wallet = HoosatCrypto.generateKeyPair('mainnet');
// Returns: { address: string, publicKey: Buffer, privateKey: Buffer }

// Import existing key pair
const importedWallet = HoosatCrypto.importKeyPair(
  privateKey: string | Buffer,
  network?: 'mainnet' | 'testnet'
);
```

### Address Operations

```typescript
// Get address from public key
const address = HoosatCrypto.publicKeyToAddress(
  publicKey: Buffer,
  network: 'mainnet' | 'testnet'
);

// Validate address
const isValid = HoosatCrypto.isValidAddress(address: string);

// Get network from address
const network = HoosatCrypto.getAddressNetwork(address: string);
// Returns: 'mainnet' | 'testnet' | null
```

### Transaction Signing

```typescript
// Sign a transaction input
const signedInput = HoosatCrypto.signTransactionInput(
  transaction: Transaction,
  inputIndex: number,
  privateKey: Buffer,
  utxo: UtxoForSigning
);

// Get transaction ID
const txId = HoosatCrypto.getTransactionId(transaction: Transaction);

// Calculate transaction hash
const hash = HoosatCrypto.calculateTransactionHash(transaction: Transaction);
```

### Hashing

```typescript
// BLAKE3 hash
const hash = HoosatCrypto.blake3Hash(data: Buffer | string);

// SHA256 hash (for legacy compatibility)
const sha256Hash = HoosatCrypto.sha256Hash(data: Buffer | string);
```

### Fee Calculation

```typescript
// Manual fee calculation
const minFee = HoosatCrypto.calculateMinFee(
  inputsCount: number,
  outputsCount: number,
  payloadSize?: number
);
```

## HoosatTxBuilder

Fluent transaction builder with automatic change calculation.

### Basic Usage

```typescript
import { HoosatTxBuilder, HoosatUtils } from 'hoosat-sdk';

const builder = new HoosatTxBuilder();

// Add inputs
for (const utxo of utxos) {
  builder.addInput(utxo, wallet.privateKey);
}

// Add outputs
builder
  .addOutput(recipientAddress, HoosatUtils.amountToSompi('1.5'))
  .setFee(minFee)
  .addChangeOutput(wallet.address);

// Build and sign
const signedTx = builder.sign();
```

### Methods

```typescript
// Add an input
builder.addInput(utxo: UtxoForSigning, privateKey: Buffer): this;

// Add an output
builder.addOutput(address: string, amount: string | bigint): this;

// Set fee
builder.setFee(fee: string | bigint): this;

// Add change output (automatically calculated)
builder.addChangeOutput(address: string): this;

// Add payload (for subnetworks)
builder.setPayload(payload: string): this;

// Sign the transaction
builder.sign(): Transaction;

// Get unsigned transaction (without signing)
builder.buildUnsigned(): Transaction;

// Get estimated transaction size
builder.estimateSize(): number;

// Validate the transaction
builder.validate(): { valid: boolean; errors: string[] };
```

## HoosatUtils

Utility functions for validation, conversion, and formatting.

### Amount Conversion

```typescript
import { HoosatUtils } from 'hoosat-sdk';

// Convert HTN to sompi (1 HTN = 100,000,000 sompi)
const sompi = HoosatUtils.amountToSompi('1.5');
// Returns: '150000000'

// Convert sompi to HTN
const htn = HoosatUtils.sompiToAmount('150000000');
// Returns: '1.5'

// Format amount for display
const formatted = HoosatUtils.formatAmount('150000000', 8);
// Returns: '1.50000000'
```

### Address Validation

```typescript
// Validate address format
const isValid = HoosatUtils.isValidAddress('hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe');

// Get network from address
const network = HoosatUtils.getAddressNetwork(address: string);
// Returns: 'mainnet' | 'testnet' | null

// Check if address is for mainnet
const isMainnet = HoosatUtils.isMainnetAddress(address: string);

// Check if address is for testnet
const isTestnet = HoosatUtils.isTestnetAddress(address: string);

// Truncate address for display
const truncated = HoosatUtils.truncateAddress(address: string, prefixLength?: number, suffixLength?: number);
// Returns: 'hoosat:qz7u...jdqe'
```

### Private Key Validation

```typescript
// Validate private key format
const isValidPrivateKey = HoosatUtils.isValidPrivateKey(privateKey: string | Buffer);

// Convert private key to buffer
const privateKeyBuffer = HoosatUtils.privateKeyToBuffer(privateKey: string | Buffer);
```

## HoosatEventManager

Real-time event streaming and WebSocket management.

### Usage

```typescript
// Subscribe to UTXO changes
await client.events.subscribeToUtxoChanges([address]);

// Listen for events
client.events.on(EventType.UtxoChange, (notification: UtxoChangeNotification) => {
  console.log('Balance changed for:', notification.address);
  console.log('Added UTXOs:', notification.added);
  console.log('Removed UTXOs:', notification.removed);
});

client.events.on(EventType.BlockAdded, (notification: BlockAddedNotification) => {
  console.log('New block:', notification.blockHash);
});

client.events.on(EventType.VirtualDagChanged, (notification) => {
  console.log('Virtual DAG changed');
});

// Unsubscribe
await client.events.unsubscribeFromUtxoChanges([address]);

// Remove event listener
client.events.off(EventType.UtxoChange, handler);
```

### Event Types

```typescript
enum EventType {
  UtxoChange = 'utxo_change',
  BlockAdded = 'block_added',
  VirtualDagChanged = 'virtual_dag_changed'
}

interface UtxoChangeNotification {
  address: string;
  added: UtxoEntry[];
  removed: UtxoEntry[];
}

interface BlockAddedNotification {
  blockHash: string;
  blockHeader: BlockHeader;
}
```

## HoosatQR

QR code generation for payments.

### Generate Payment QR

```typescript
import { HoosatQR, HoosatUtils } from 'hoosat-sdk';

const qr = await HoosatQR.generatePaymentQR({
  address: string;
  amount?: string | bigint;  // Amount in sompi
  label?: string;
  message?: string;
}, {
  width?: number;
  height?: number;
  color?: string;
  backgroundColor?: string;
});

// Returns: data URL of QR code image
```

### Generate Address QR

```typescript
const qr = await HoosatQR.generateAddressQR(
  address: string,
  options?: QRCodeOptions
);
```

### Payment URI

```typescript
// Build payment URI
const uri = HoosatQR.buildPaymentURI({
  address: string;
  amount?: string | bigint;
  label?: string;
  message?: string;
});
// Returns: 'hoosat:address?amount=1.5&label=Store'

// Parse payment URI
const params = HoosatQR.parsePaymentURI(uri: string);
// Returns: { address, amount?, label?, message? }
```

## HoosatSigner

Message signing and verification for authentication.

### Sign Message

```typescript
import { HoosatSigner } from 'hoosat-sdk';

const signature = HoosatSigner.signMessage(
  message: string,
  privateKey: Buffer
);

// Returns: hex-encoded signature string
```

### Verify Message

```typescript
const isValid = HoosatSigner.verifyMessage(
  message: string,
  signature: string,
  publicKey: Buffer
);

// Returns: boolean
```

### Create Signed Message Object

```typescript
const signedMessage = HoosatSigner.createSignedMessage(
  message: string,
  signature: string,
  address: string
);

// Returns: { message, signature, address }
```

### Verify Signed Message

```typescript
const isValid = HoosatSigner.verifySignedMessage(signedMessage: SignedMessage);

// Returns: boolean
```

## Error Handling

All SDK methods use a consistent error handling pattern:

```typescript
interface BaseResult<T> {
  ok: boolean;
  result?: T;
  error?: string;
}

// Usage pattern
const result = await client.getBalance(address);

if (result.ok) {
  // Success - use result.result
  console.log('Balance:', result.result.balance);
} else {
  // Error - check result.error
  console.error('Error:', result.error);
}
```

**Benefits:**
- Type-safe error handling
- No thrown exceptions for API calls
- Explicit success/failure checking
- Detailed error messages

## Complete Transaction Example

```typescript
import {
  HoosatClient,
  HoosatCrypto,
  HoosatTxBuilder,
  HoosatUtils
} from 'hoosat-sdk';

async function sendHoosat(
  senderPrivateKey: string,
  recipientAddress: string,
  amountHtn: string
) {
  // Initialize
  const client = new HoosatClient({
    host: '54.38.176.95',
    port: 42420
  });
  
  const wallet = HoosatCrypto.importKeyPair(senderPrivateKey, 'mainnet');
  
  try {
    // Get UTXOs
    const utxosResult = await client.getUtxosByAddresses([wallet.address]);
    if (!utxosResult.ok) {
      throw new Error(utxosResult.error);
    }
    
    // Calculate minimum fee
    const feeResult = await client.calculateMinFee(wallet.address);
    if (!feeResult.ok) {
      throw new Error(feeResult.error);
    }
    
    // Build transaction
    const builder = new HoosatTxBuilder();
    
    for (const utxo of utxosResult.result.utxos) {
      builder.addInput(utxo, wallet.privateKey);
    }
    
    builder
      .addOutput(recipientAddress, HoosatUtils.amountToSompi(amountHtn))
      .setFee(feeResult.result.fee)
      .addChangeOutput(wallet.address);
    
    // Sign
    const signedTx = builder.sign();
    
    // Submit
    const submitResult = await client.submitTransaction(signedTx);
    if (!submitResult.ok) {
      throw new Error(submitResult.error);
    }
    
    console.log('Transaction submitted:', submitResult.result.transactionId);
    return submitResult.result.transactionId;
    
  } finally {
    await client.disconnect();
  }
}
```

## Constants

```typescript
// Unit conversion
const SOMPI_PER_HTN = 100000000n;  // 1 HTN = 100,000,000 sompi

// Network prefixes
const MAINNET_PREFIX = 'hoosat:';
const TESTNET_PREFIX = 'hoosattest:';

// Address versions
const ADDRESS_VERSION_SCHNORR = 0x00;
const ADDRESS_VERSION_ECDSA = 0x01;
const ADDRESS_VERSION_P2SH = 0x08;

// Transaction limits
const MAX_RECIPIENT_OUTPUTS = 2;
const MAX_TOTAL_OUTPUTS = 3;

// Dust threshold
const DUST_THRESHOLD = 1000n;  // 1000 sompi
```

## Type Definitions

### Core Types

```typescript
// Network type
type HoosatNetwork = 'mainnet' | 'testnet';

// Key pair
interface KeyPair {
  address: string;
  publicKey: Buffer;
  privateKey: Buffer;
}

// UTXO entry
interface UtxoForSigning {
  outpoint: {
    transactionId: string;
    index: number;
  };
  utxoEntry: {
    amount: string;
    scriptPublicKey: {
      scriptPublicKey: string;
      version: number;
    };
    blockDaaScore: string;
    isCoinbase: boolean;
  };
}

// Transaction
interface Transaction {
  version: number;
  inputs: TransactionInput[];
  outputs: TransactionOutput[];
  lockTime: string;
  subnetworkId: string;
  gas: string;
  payload: string;
}

interface TransactionInput {
  previousOutpoint: {
    transactionId: string;
    index: number;
  };
  signatureScript: string;
  sequence: number;
  sigOpCount: number;
}

interface TransactionOutput {
  amount: string;
  scriptPublicKey: {
    scriptPublicKey: string;
    version: number;
  };
}
```

## Links

- **NPM Package**: https://www.npmjs.com/package/hoosat-sdk
- **GitHub**: https://github.com/Hoosat-Oy/hoosat-sdk
- **Developer Hub**: https://hub.hoosat.net/
- **API Docs**: https://proxy.hoosat.net/docs
