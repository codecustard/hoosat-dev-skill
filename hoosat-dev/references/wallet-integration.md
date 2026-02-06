# Wallet Integration Guide

Guide for integrating Hoosat wallet functionality into applications.

## Overview

Hoosat wallet integration supports multiple environments:
- **Browser dApps**: Using `hoosat-sdk-web` for React/Vue/Angular apps
- **Node.js backends**: Using `hoosat-sdk` for server-side wallets
- **Internet Computer**: Using `hoosat-mo` for IC canisters

## Connection Patterns

### Browser Wallet Adapter Pattern

```typescript
// types.ts
interface HoosatWalletAdapter {
  connect(): Promise<string>;  // Returns address
  disconnect(): Promise<void>;
  getAddress(): string | null;
  getBalance(): Promise<string>;
  signTransaction(tx: Transaction): Promise<Transaction>;
  signMessage(message: string): Promise<string>;
  on(event: string, callback: Function): void;
  off(event: string, callback: Function): void;
}

// events: 'connect', 'disconnect', 'balanceChange'
```

### Implementation Example

```typescript
// HoosatWalletAdapter.ts
import {
  HoosatWebClient,
  HoosatCrypto,
  HoosatTxBuilder,
  HoosatUtils,
  HoosatSigner,
  HoosatQR
} from 'hoosat-sdk-web';
import { EventEmitter } from 'events';

export class HoosatWalletAdapter extends EventEmitter implements HoosatWalletAdapter {
  private client: HoosatWebClient;
  private wallet: KeyPair | null = null;
  private connected = false;

  constructor() {
    super();
    this.client = new HoosatWebClient({
      baseUrl: 'https://proxy.hoosat.net/api/v1'
    });
  }

  // Connect with private key (for demo/testing)
  async connectWithPrivateKey(privateKey: string): Promise<string> {
    this.wallet = HoosatCrypto.importKeyPair(privateKey, 'mainnet');
    this.connected = true;
    this.emit('connect', this.wallet.address);
    
    // Start balance monitoring
    this.startBalanceMonitoring();
    
    return this.wallet.address;
  }

  // Generate new wallet
  async createWallet(): Promise<{ address: string; privateKey: string }> {
    this.wallet = HoosatCrypto.generateKeyPair('mainnet');
    this.connected = true;
    
    this.emit('connect', this.wallet.address);
    this.startBalanceMonitoring();
    
    return {
      address: this.wallet.address,
      privateKey: this.wallet.privateKey.toString('hex')
    };
  }

  async disconnect(): Promise<void> {
    this.wallet = null;
    this.connected = false;
    this.emit('disconnect');
  }

  getAddress(): string | null {
    return this.wallet?.address || null;
  }

  async getBalance(): Promise<string> {
    if (!this.wallet) throw new Error('Not connected');
    const balance = await this.client.getBalance(this.wallet.address);
    return HoosatUtils.sompiToAmount(balance);
  }

  async signTransaction(tx: Transaction): Promise<Transaction> {
    if (!this.wallet) throw new Error('Not connected');
    // Transaction signing logic here
    return tx;
  }

  async signMessage(message: string): Promise<string> {
    if (!this.wallet) throw new Error('Not connected');
    return HoosatSigner.signMessage(this.wallet.privateKey, message);
  }

  async sendTransaction(
    recipientAddress: string,
    amountHtn: string,
    fee?: string
  ): Promise<string> {
    if (!this.wallet) throw new Error('Not connected');

    // Get UTXOs
    const utxos = await this.client.getUtxos([this.wallet.address]);

    // Get fee estimate if not provided
    const feeEstimate = await this.client.getFeeEstimate();
    const txFee = fee || feeEstimate.normalBucket.feeRate.toString();

    // Build transaction
    const builder = new HoosatTxBuilder();
    utxos.forEach(utxo => builder.addInput(utxo, this.wallet!.privateKey));

    builder
      .addOutput(recipientAddress, HoosatUtils.amountToSompi(amountHtn))
      .setFee(txFee)
      .addChangeOutput(this.wallet.address);

    // Sign and submit
    const signedTx = builder.sign();
    const txId = await this.client.submitTransaction(signedTx);

    this.emit('transactionSent', { txId, recipient: recipientAddress, amount: amountHtn });

    return txId;
  }

  async generatePaymentQR(amountHtn?: string): Promise<string> {
    if (!this.wallet) throw new Error('Not connected');
    
    return HoosatQR.generatePaymentQR({
      address: this.wallet.address,
      amount: amountHtn ? HoosatUtils.amountToSompi(amountHtn) : undefined
    });
  }

  private async startBalanceMonitoring(): Promise<void> {
    // Poll balance every 30 seconds
    setInterval(async () => {
      if (this.wallet) {
        const balance = await this.getBalance();
        this.emit('balanceChange', balance);
      }
    }, 30000);
  }
}
```

## React Hook Example

```typescript
// useHoosatWallet.ts
import { useState, useEffect, useCallback } from 'react';
import { HoosatWalletAdapter } from './HoosatWalletAdapter';

export function useHoosatWallet() {
  const [adapter] = useState(() => new HoosatWalletAdapter());
  const [connected, setConnected] = useState(false);
  const [address, setAddress] = useState<string | null>(null);
  const [balance, setBalance] = useState<string>('0');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const handleConnect = (addr: string) => {
      setConnected(true);
      setAddress(addr);
      updateBalance();
    };

    const handleDisconnect = () => {
      setConnected(false);
      setAddress(null);
      setBalance('0');
    };

    const handleBalanceChange = (newBalance: string) => {
      setBalance(newBalance);
    };

    adapter.on('connect', handleConnect);
    adapter.on('disconnect', handleDisconnect);
    adapter.on('balanceChange', handleBalanceChange);

    return () => {
      adapter.off('connect', handleConnect);
      adapter.off('disconnect', handleDisconnect);
      adapter.off('balanceChange', handleBalanceChange);
    };
  }, [adapter]);

  const connect = useCallback(async (privateKey: string) => {
    setLoading(true);
    try {
      await adapter.connectWithPrivateKey(privateKey);
    } finally {
      setLoading(false);
    }
  }, [adapter]);

  const disconnect = useCallback(async () => {
    await adapter.disconnect();
  }, [adapter]);

  const updateBalance = useCallback(async () => {
    if (adapter.getAddress()) {
      const bal = await adapter.getBalance();
      setBalance(bal);
    }
  }, [adapter]);

  const send = useCallback(async (recipient: string, amount: string) => {
    return adapter.sendTransaction(recipient, amount);
  }, [adapter]);

  return {
    connected,
    address,
    balance,
    loading,
    connect,
    disconnect,
    send,
    refreshBalance: updateBalance
  };
}
```

## React Component Example

```tsx
// WalletConnect.tsx
import { useHoosatWallet } from './useHoosatWallet';

export function WalletConnect() {
  const { connected, address, balance, loading, connect, disconnect } = useHoosatWallet();

  if (!connected) {
    return (
      <div>
        <button onClick={() => {
          const key = prompt('Enter private key:');
          if (key) connect(key);
        }} disabled={loading}>
          {loading ? 'Connecting...' : 'Connect Wallet'}
        </button>
      </div>
    );
  }

  return (
    <div>
      <p>Address: {address}</p>
      <p>Balance: {balance} HTN</p>
      <button onClick={disconnect}>Disconnect</button>
    </div>
  );
}
```

## MetaMask-Style Integration

For browser extension wallet integration:

```typescript
// Check if Hoosat wallet extension is installed
const isHoosatWalletInstalled = (): boolean => {
  return typeof window.hoosat !== 'undefined';
};

// Connect to extension
const connectToExtension = async (): Promise<string> => {
  if (!isHoosatWalletInstalled()) {
    throw new Error('Hoosat wallet extension not installed');
  }

  try {
    const accounts = await window.hoosat.request({
      method: 'hoosat_requestAccounts'
    });
    return accounts[0];
  } catch (error) {
    throw new Error('User rejected connection');
  }
};

// Sign transaction with extension
const signWithExtension = async (tx: Transaction): Promise<Transaction> => {
  return window.hoosat.request({
    method: 'hoosat_signTransaction',
    params: [tx]
  });
};

// Window type augmentation
declare global {
  interface Window {
    hoosat?: {
      request: (args: { method: string; params?: any[] }) => Promise<any>;
    };
  }
}
```

## Security Best Practices

### 1. Never Store Private Keys in Local Storage

```typescript
// BAD
localStorage.setItem('privateKey', privateKey);

// GOOD - Use secure storage or session only
// Store in memory only during session
// Or use encrypted storage with user password
```

### 2. Validate All Addresses

```typescript
import { HoosatUtils } from 'hoosat-sdk-web';

const send = async (recipient: string, amount: string) => {
  if (!HoosatUtils.isValidAddress(recipient)) {
    throw new Error('Invalid recipient address');
  }
  
  // Check network
  const network = HoosatUtils.getAddressNetwork(recipient);
  if (network !== 'mainnet') {
    throw new Error('Only mainnet addresses supported');
  }
  
  // Proceed with transaction...
};
```

### 3. Confirm Transactions

```typescript
const confirmAndSend = async (recipient: string, amount: string) => {
  const confirmed = window.confirm(
    `Send ${amount} HTN to ${recipient}?`
  );
  
  if (!confirmed) {
    throw new Error('Transaction cancelled by user');
  }
  
  return sendTransaction(recipient, amount);
};
```

### 4. Handle Errors Gracefully

```typescript
try {
  const txId = await adapter.sendTransaction(recipient, amount);
  showSuccess(`Transaction sent! ID: ${txId}`);
} catch (error) {
  if (error.message.includes('Insufficient funds')) {
    showError('Insufficient balance for this transaction');
  } else if (error.message.includes('Invalid address')) {
    showError('Please enter a valid Hoosat address');
  } else {
    showError('Transaction failed: ' + error.message);
  }
}
```

## Testing Integration

### Testnet Setup

```typescript
// Use testnet for development
const TESTNET_CONFIG = {
  network: 'testnet',
  prefix: 'hoosattest:',
  apiUrl: 'https://proxy.hoosat.net/api/v1',  // Testnet endpoint
  faucetUrl: 'https://faucet.hoosat.net'      // Get test HTN
};

// Create testnet wallet
const testWallet = HoosatCrypto.generateKeyPair('testnet');
```

### Mock Wallet for Testing

```typescript
// MockHoosatWallet.ts
export class MockHoosatWallet {
  private balance = '1000';
  private transactions: string[] = [];

  async connect(): Promise<string> {
    return 'hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe';
  }

  async getBalance(): Promise<string> {
    return this.balance;
  }

  async sendTransaction(recipient: string, amount: string): Promise<string> {
    this.balance = (parseFloat(this.balance) - parseFloat(amount)).toString();
    const txId = 'mock-tx-' + Date.now();
    this.transactions.push(txId);
    return txId;
  }
}
```

## Links

- **SDK Web**: https://www.npmjs.com/package/hoosat-sdk-web
- **SDK Node.js**: https://www.npmjs.com/package/hoosat-sdk
- **Developer Hub**: https://hub.hoosat.net/docs/wallet-extension
