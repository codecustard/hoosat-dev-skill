# Hoosat Browser SDK (hoosat-sdk-web)

Complete reference for the Hoosat Browser SDK using REST API connections.

## Installation

```bash
npm install hoosat-sdk-web
# or
yarn add hoosat-sdk-web
```

## Quick Start

```typescript
import { HoosatWebClient, HoosatCrypto, HoosatUtils } from 'hoosat-sdk-web';

// Create client
const client = new HoosatWebClient({
  baseUrl: 'https://proxy.hoosat.net/api/v1'
});

// Generate wallet
const wallet = HoosatCrypto.generateKeyPair('mainnet');
console.log('Address:', wallet.address);

// Check balance
const balance = await client.getBalance(wallet.address);
console.log('Balance:', HoosatUtils.sompiToAmount(balance), 'HTN');
```

## HoosatWebClient

REST API client for browser environments.

### Constructor

```typescript
const client = new HoosatWebClient({
  baseUrl: string;  // API base URL
});

// Default: https://proxy.hoosat.net/api/v1
```

### Balance Operations

#### Get Balance

```typescript
const balance: string = await client.getBalance(address: string);
// Returns balance in sompi as string
```

#### Get Balances

```typescript
const balances = await client.getBalances(addresses: string[]);
// Returns: Array of { address: string, balance: string }
```

### UTXO Operations

#### Get UTXOs

```typescript
const utxos = await client.getUtxos(addresses: string[]);
// Returns: UtxoForSigning[]
```

### Transaction Operations

#### Submit Transaction

```typescript
const transactionId: string = await client.submitTransaction(transaction: Transaction);
// Returns: Transaction ID
```

#### Get Transaction Status

```typescript
const status = await client.getTransactionStatus(transactionId: string);
// Returns: { transactionId, status, confirmingBlockHash?, confirmingBlockBlueScore? }
```

### Fee Estimation

```typescript
const feeEstimate = await client.getFeeEstimate();
// Returns: { priorityBucket, normalBucket, lowBucket }
```

### Network Operations

```typescript
// Get network info
const networkInfo = await client.getNetworkInfo();
// Returns: { network, ... }

// Get node info
const nodeInfo = await client.getNodeInfo();
// Returns: { p2pId, mempoolSize, serverVersion, isUtxoIndexed, isSynced }

// Get coin supply
const supply = await client.getCoinSupply();
// Returns: { circulatingSupply, maxSupply }
```

### Block Operations

```typescript
// Get block by hash
const block = await client.getBlock(hash: string);

// Get blocks
const blocks = await client.getBlocks(lowHash: string);

// Get tip hash
const tipHash = await client.getTipHash();

// Get blue score
const blueScore = await client.getBlueScore();
```

### Mempool Operations

```typescript
// Get mempool entries
const entries = await client.getMempoolEntries();

// Get mempool entry
const entry = await client.getMempoolEntry(transactionId: string);

// Get mempool entries by addresses
const addressEntries = await client.getMempoolEntriesByAddresses(addresses: string[]);
```

## HoosatCrypto (Browser)

Cryptographic operations for browser environments using BLAKE3.

### Key Generation

```typescript
import { HoosatCrypto } from 'hoosat-sdk-web';

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

// BLAKE3 hash
const hash = HoosatCrypto.blake3Hash(data: Buffer | string);
```

## HoosatTxBuilder (Browser)

Transaction builder for browser environments.

### Basic Usage

```typescript
import { HoosatTxBuilder, HoosatUtils } from 'hoosat-sdk-web';

const builder = new HoosatTxBuilder();

// Add inputs
utxos.forEach(utxo => builder.addInput(utxo, wallet.privateKey));

// Add outputs
builder
  .addOutput(recipientAddress, HoosatUtils.amountToSompi('1.5'))
  .setFee(fee)
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

// Add change output
builder.addChangeOutput(address: string): this;

// Set payload
builder.setPayload(payload: string): this;

// Sign the transaction
builder.sign(): Transaction;

// Build unsigned transaction
builder.buildUnsigned(): Transaction;

// Validate the transaction
builder.validate(): { valid: boolean; errors: string[] };
```

## HoosatUtils (Browser)

Utility functions for browser environments.

### Amount Conversion

```typescript
import { HoosatUtils } from 'hoosat-sdk-web';

// Convert HTN to sompi
const sompi = HoosatUtils.amountToSompi('1.5');
// Returns: '150000000'

// Convert sompi to HTN
const htn = HoosatUtils.sompiToAmount('150000000');
// Returns: '1.5'

// Format amount
const formatted = HoosatUtils.formatAmount('150000000', 8);
// Returns: '1.50000000'
```

### Address Validation

```typescript
// Validate address
const isValid = HoosatUtils.isValidAddress(address: string);

// Get network from address
const network = HoosatUtils.getAddressNetwork(address: string);

// Check mainnet
const isMainnet = HoosatUtils.isMainnetAddress(address: string);

// Check testnet
const isTestnet = HoosatUtils.isTestnetAddress(address: string);

// Truncate for display
const truncated = HoosatUtils.truncateAddress(address: string);
// Returns: 'hoosat:qz7u...jdqe'
```

## HoosatSigner (Browser)

Message signing for authentication in browser.

### Sign Message

```typescript
import { HoosatSigner } from 'hoosat-sdk-web';

const signature = HoosatSigner.signMessage(
  privateKey: string | Buffer,
  message: string
);

// Returns: hex-encoded signature
```

### Verify Message

```typescript
const isValid = HoosatSigner.verifyMessage(
  signature: string,
  message: string,
  publicKey: string | Buffer
);

// Returns: boolean
```

### Create Signed Message

```typescript
const signedMessage = HoosatSigner.createSignedMessage(
  privateKey: string | Buffer,
  message: string,
  address: string
);

// Returns: { message, signature, address }
```

### Verify Signed Message

```typescript
const isValid = HoosatSigner.verifySignedMessage(signedMessage: SignedMessage);

// Returns: boolean
```

## HoosatQR (Browser)

QR code generation in browser.

### Generate Payment QR

```typescript
import { HoosatQR, HoosatUtils } from 'hoosat-sdk-web';

const qrDataUrl = await HoosatQR.generatePaymentQR({
  address: merchantAddress,
  amount: HoosatUtils.amountToSompi('1.5'),
  label: 'My Store',
  message: 'Order #12345'
}, {
  width: 256,
  height: 256,
  color: '#000000',
  backgroundColor: '#ffffff'
});

// Returns: data URL for img src
```

### Generate Address QR

```typescript
const qrDataUrl = await HoosatQR.generateAddressQR(
  address: string,
  options?: QRCodeOptions
);
```

### Payment URI

```typescript
// Build URI
const uri = HoosatQR.buildPaymentURI({
  address: string,
  amount?: string | bigint,
  label?: string,
  message?: string
});

// Parse URI
const params = HoosatQR.parsePaymentURI(uri: string);
```

## Complete Transaction Example (Browser)

```typescript
import {
  HoosatWebClient,
  HoosatCrypto,
  HoosatTxBuilder,
  HoosatUtils
} from 'hoosat-sdk-web';

async function sendHoosat(
  senderPrivateKey: string,
  recipientAddress: string,
  amountHtn: string
) {
  // Initialize
  const client = new HoosatWebClient({
    baseUrl: 'https://proxy.hoosat.net/api/v1'
  });
  
  const wallet = HoosatCrypto.importKeyPair(senderPrivateKey, 'mainnet');
  
  // Get UTXOs
  const utxos = await client.getUtxos([wallet.address]);
  
  // Get fee estimate
  const feeEstimate = await client.getFeeEstimate();
  const fee = feeEstimate.normalBucket.feeRate;
  
  // Build transaction
  const builder = new HoosatTxBuilder();
  
  utxos.forEach(utxo => {
    builder.addInput(utxo, wallet.privateKey);
  });
  
  builder
    .addOutput(recipientAddress, HoosatUtils.amountToSompi(amountHtn))
    .setFee(fee)
    .addChangeOutput(wallet.address);
  
  // Sign
  const signedTx = builder.sign();
  
  // Submit
  const txId = await client.submitTransaction(signedTx);
  
  console.log('Transaction submitted:', txId);
  return txId;
}
```

## Wallet Integration Example

```typescript
import { HoosatWebClient, HoosatCrypto, HoosatUtils } from 'hoosat-sdk-web';

class HoosatWallet {
  private client: HoosatWebClient;
  private wallet: KeyPair | null = null;
  
  constructor() {
    this.client = new HoosatWebClient({
      baseUrl: 'https://proxy.hoosat.net/api/v1'
    });
  }
  
  // Create new wallet
  createWallet(network: 'mainnet' | 'testnet' = 'mainnet') {
    this.wallet = HoosatCrypto.generateKeyPair(network);
    return this.wallet.address;
  }
  
  // Import wallet
  importWallet(privateKey: string, network: 'mainnet' | 'testnet' = 'mainnet') {
    this.wallet = HoosatCrypto.importKeyPair(privateKey, network);
    return this.wallet.address;
  }
  
  // Get balance
  async getBalance(): Promise<string> {
    if (!this.wallet) throw new Error('No wallet');
    const balance = await this.client.getBalance(this.wallet.address);
    return HoosatUtils.sompiToAmount(balance);
  }
  
  // Get address
  getAddress(): string {
    if (!this.wallet) throw new Error('No wallet');
    return this.wallet.address;
  }
  
  // Check if connected
  isConnected(): boolean {
    return this.wallet !== null;
  }
}

// Usage
const wallet = new HoosatWallet();
const address = wallet.createWallet('mainnet');
console.log('Address:', address);

const balance = await wallet.getBalance();
console.log('Balance:', balance, 'HTN');
```

## Constants

```typescript
// Unit conversion
const SOMPI_PER_HTN = 100000000n;

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
const DUST_THRESHOLD = 1000n;
```

## Type Definitions

```typescript
// Network type
type HoosatNetwork = 'mainnet' | 'testnet';

// Key pair
interface KeyPair {
  address: string;
  publicKey: Buffer;
  privateKey: Buffer;
}

// UTXO
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

// Fee estimate
interface FeeEstimate {
  priorityBucket: {
    feeRate: number;
    estimatedSeconds: number;
  };
  normalBucket: {
    feeRate: number;
    estimatedSeconds: number;
  };
  lowBucket: {
    feeRate: number;
    estimatedSeconds: number;
  };
}
```

## Links

- **NPM Package**: https://www.npmjs.com/package/hoosat-sdk-web
- **GitHub**: https://github.com/Hoosat-Oy/hoosat-sdk-web
- **Developer Hub**: https://hub.hoosat.net/docs/sdk-web
- **API Docs**: https://proxy.hoosat.net/docs
