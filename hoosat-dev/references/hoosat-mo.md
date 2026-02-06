# Hoosat Motoko Package (hoosat-mo)

Complete reference for the Hoosat Motoko package for Internet Computer development.

## Installation

Install via Mops (Motoko Package Manager):

```bash
mops install hoosat-mo
```

Add to your `mops.toml`:
```toml
[dependencies]
hoosat-mo = "0.2.3"
```

## Quick Start

```motoko
import Wallet "mo:hoosat-mo/wallet";
import Address "mo:hoosat-mo/address";
import HoosatUtils "mo:hoosat-mo/utils";

// Create mainnet wallet
let wallet = Wallet.createMainnetWallet("my-key", ?"hoosat");

// Get balance
let balanceResult = await wallet.getBalance("hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe");

switch (balanceResult) {
  case (#ok(balance)) {
    Debug.print("Balance: " # debug_show(balance));
  };
  case (#err(error)) {
    Debug.print("Error: " # Errors.errorToText(error));
  };
};
```

## Module Overview

### Core Modules

| Module | Purpose | Import Path |
|--------|---------|-------------|
| **Wallet** | High-level wallet operations | `mo:hoosat-mo/wallet` |
| **Address** | Address generation and validation | `mo:hoosat-mo/address` |
| **Validation** | Input validation | `mo:hoosat-mo/validation` |
| **Transaction** | Transaction building | `mo:hoosat-mo/transaction` |
| **Errors** | Error handling | `mo:hoosat-mo/errors` |
| **Types** | Type definitions | `mo:hoosat-mo/types` |
| **Sighash** | Signature hash calculation | `mo:hoosat-mo/sighash` |
| **PersonalMessage** | Message signing | `mo:hoosat-mo/personal-message` |

## Wallet Module

High-level wallet operations for the Internet Computer.

### Creating a Wallet

```motoko
import Wallet "mo:hoosat-mo/wallet";

// Create mainnet wallet
let mainnetWallet = Wallet.createMainnetWallet("unique-key", ?"hoosat");

// Create testnet wallet
let testnetWallet = Wallet.createTestnetWallet("unique-key", ?"hoosat");
```

### Wallet Methods

```motoko
// Get balance
let balanceResult = await wallet.getBalance(address: Text);
// Returns: Result<Nat64, HoosatError>

// Send transaction
let txResult = await wallet.sendTransaction(
  from: Text,           // Sender address
  to: Text,             // Recipient address
  amount: Nat64,        // Amount in sompi
  fee: ?Nat64,          // Optional fee (null for auto)
  payload: ?Text        // Optional payload
);
// Returns: Result<Text, HoosatError> (transaction ID)

// Get UTXOs
let utxosResult = await wallet.getUtxos(address: Text);
// Returns: Result<[UTXO], HoosatError>
```

### Complete Wallet Example

```motoko
import Wallet "mo:hoosat-mo/wallet";
import Errors "mo:hoosat-mo/errors";
import Debug "mo:base/Debug";

actor {
  let wallet = Wallet.createMainnetWallet("my-app-key", ?"hoosat");
  
  public func checkBalance(address: Text) : async Text {
    let result = await wallet.getBalance(address);
    
    switch (result) {
      case (#ok(balance)) {
        return "Balance: " # debug_show(balance) # " sompi";
      };
      case (#err(error)) {
        return "Error: " # Errors.errorToText(error);
      };
    };
  };
  
  public func sendHoosat(
    from: Text,
    to: Text,
    amount: Nat64
  ) : async Text {
    let result = await wallet.sendTransaction(from, to, amount, null, null);
    
    switch (result) {
      case (#ok(txId)) {
        return "Transaction sent: " # txId;
      };
      case (#err(error)) {
        return "Error: " # Errors.errorToText(error);
      };
    };
  };
};
```

## Address Module

Address generation, validation, and encoding.

### Address Types

```motoko
import Address "mo:hoosat-mo/address";

// Address type constants
Address.SCHNORR  // = 0 (32-byte pubkey)
Address.ECDSA    // = 1 (33-byte pubkey)
Address.P2SH     // = 2 (Pay-to-Script-Hash)
```

### Generating Addresses

```motoko
// Generate address from public key
let address = Address.fromPublicKey(
  publicKey: [Nat8],
  network: Text,       // "mainnet" or "testnet"
  addressType: Nat8    // Address.SCHNORR, Address.ECDSA, or Address.P2SH
);

// Generate random address
let randomAddress = Address.generate(network: Text, addressType: Nat8);
```

### Address Validation

```motoko
// Validate address format
let isValid = Address.isValid(address: Text);

// Get network from address
let network = Address.getNetwork(address: Text);
// Returns: ?Text ("mainnet" or "testnet")

// Get address type
let addrType = Address.getType(address: Text);
// Returns: ?Nat8

// Check if mainnet
let isMainnet = Address.isMainnet(address: Text);

// Check if testnet
let isTestnet = Address.isTestnet(address: Text);
```

### Address Encoding/Decoding

```motoko
// Decode address to get components
let decoded = Address.decode(address: Text);
// Returns: {
//   prefix: Text;
//   version: Nat8;
//   payload: [Nat8];
// }

// Encode components to address
let address = Address.encode(
  prefix: Text,
  version: Nat8,
  payload: [Nat8]
);
```

## Validation Module

Input validation and security checks.

### Address Validation

```motoko
import Validation "mo:hoosat-mo/validation";

// Validate address
let result = Validation.validateAddress(address: Text);
// Returns: Result<(), HoosatError>

switch (result) {
  case (#ok(())) { /* Valid */ };
  case (#err(#InvalidAddress(msg))) { /* Invalid */ };
  case (#err(error)) { /* Other error */ };
};
```

### Amount Validation

```motoko
// Validate amount
let result = Validation.validateAmount(amount: Nat64);
// Returns: Result<(), HoosatError>

// Validate amount string
let result = Validation.validateAmountText(amountText: Text);
// Returns: Result<Nat64, HoosatError>
```

### Transaction Validation

```motoko
// Validate transaction
let result = Validation.validateTransaction(tx: HoosatTransaction);
// Returns: Result<(), HoosatError>
```

### Private Key Validation

```motoko
// Validate private key
let result = Validation.validatePrivateKey(privateKey: [Nat8]);
// Returns: Result<(), HoosatError>
```

## Transaction Module

Transaction building and serialization.

### Building Transactions

```motoko
import Transaction "mo:hoosat-mo/transaction";

// Build simple transaction
let tx = Transaction.buildTransaction(
  utxo: UTXO,
  recipientScript: Text,
  amount: Nat64,
  fee: Nat64,
  changeScript: ?Text
);
// Returns: HoosatTransaction

// Add input
let txWithInput = Transaction.addInput(
  tx: HoosatTransaction,
  utxo: UTXO
);

// Add output
let txWithOutput = Transaction.addOutput(
  tx: HoosatTransaction,
  scriptPublicKey: Text,
  amount: Nat64
);
```

### Transaction Serialization

```motoko
// Serialize transaction to bytes
let bytes = Transaction.serialize(tx: HoosatTransaction);
// Returns: [Nat8]

// Deserialize transaction from bytes
let tx = Transaction.deserialize(bytes: [Nat8]);
// Returns: ?HoosatTransaction

// Get transaction ID
let txId = Transaction.getId(tx: HoosatTransaction);
// Returns: Text
```

### Transaction Validation

```motoko
// Check if transaction is valid
let isValid = Transaction.isValid(tx: HoosatTransaction);

// Get transaction size
let size = Transaction.getSize(tx: HoosatTransaction);
// Returns: Nat32
```

## Errors Module

Comprehensive error handling.

### Error Types

```motoko
import Errors "mo:hoosat-mo/errors";

type HoosatError = {
  #InvalidAddress: Text;
  #InvalidAmount: Text;
  #InsufficientFunds: { available: Nat64; required: Nat64 };
  #NetworkError: Text;
  #SigningError: Text;
  #ValidationError: Text;
  #InternalError: Text;
};
```

### Error Handling

```motoko
// Convert error to text
let errorText = Errors.errorToText(error: HoosatError);

// Pattern matching on errors
switch (result) {
  case (#ok(value)) {
    // Handle success
  };
  case (#err(#InvalidAddress(msg))) {
    Debug.print("Invalid address: " # msg);
  };
  case (#err(#InsufficientFunds(info))) {
    Debug.print("Need: " # debug_show(info.required));
    Debug.print("Have: " # debug_show(info.available));
  };
  case (#err(#NetworkError(msg))) {
    Debug.print("Network error: " # msg);
  };
  case (#err(error)) {
    Debug.print("Error: " # Errors.errorToText(error));
  };
};
```

## Types Module

Core data structures and type definitions.

### Core Types

```motoko
import Types "mo:hoosat-mo/types";

// UTXO type
type UTXO = {
  transactionId: Text;
  index: Nat32;
  amount: Nat64;
  scriptVersion: Nat16;
  scriptPublicKey: Text;
  address: Text;
};

// Transaction input
type TransactionInput = {
  previousOutpoint: {
    transactionId: Text;
    index: Nat32;
  };
  signatureScript: Text;
  sequence: Nat32;
  sigOpCount: Nat8;
};

// Transaction output
type TransactionOutput = {
  amount: Nat64;
  scriptPublicKey: {
    scriptPublicKey: Text;
    version: Nat16;
  };
};

// Complete transaction
type HoosatTransaction = {
  version: Nat16;
  inputs: [TransactionInput];
  outputs: [TransactionOutput];
  lockTime: Nat64;
  subnetworkId: Text;
  gas: Nat64;
  payload: Text;
};
```

### Result Types

```motoko
// Standard result type
type Result<T, E> = {
  #ok: T;
  #err: E;
};

// Hoosat result
type HoosatResult<T> = Result<T, HoosatError>;
```

## Sighash Module

Signature hash calculation for Schnorr and ECDSA signatures.

### Sighash Types

```motoko
import Sighash "mo:hoosat-mo/sighash";

// Sighash type constants
Sighash.SigHashAll                  // 0x01 - Signs all inputs and outputs
Sighash.SigHashNone                 // 0x02 - Signs inputs only
Sighash.SigHashSingle               // 0x04 - Signs inputs and one output
Sighash.SigHashAnyOneCanPay         // 0x80 - Signs only current input
Sighash.SigHashAll_AnyOneCanPay     // 0x81 - Combination
Sighash.SigHashNone_AnyOneCanPay    // 0x82 - Combination
Sighash.SigHashSingle_AnyOneCanPay  // 0x84 - Combination
```

### Calculating Sighashes

```motoko
// Calculate sighash for ECDSA
let hash = Sighash.calculateSighashEcdsa(
  tx: HoosatTransaction,
  inputIndex: Nat32,
  utxo: UTXO,
  sighashType: Nat8,
  reusedValues: SighashReusedValues
);
// Returns: [Nat8]

// Calculate sighash for Schnorr
let hash = Sighash.calculateSighashSchnorr(
  tx: HoosatTransaction,
  inputIndex: Nat32,
  utxo: UTXO,
  sighashType: Nat8,
  reusedValues: SighashReusedValues
);
// Returns: [Nat8]
```

### Reused Values (Optimization)

```motoko
// Create reused values for efficiency
let reusedValues : Sighash.SighashReusedValues = {
  var previousOutputsHash = null;
  var sequencesHash = null;
  var sigOpCountsHash = null;
  var outputsHash = null;
  var payloadHash = null;
};

// Calculate multiple sighashes efficiently
for (i in inputs.keys()) {
  let hash = Sighash.calculateSighashEcdsa(
    tx, 
    Nat32.fromNat(i), 
    utxos[i], 
    Sighash.SigHashAll, 
    reusedValues
  );
  // Use hash for signing...
};
```

## Personal Message Module

Personal message signing and verification.

### Signing Messages

```motoko
import PersonalMessage "mo:hoosat-mo/personal-message";

// Sign a message
let signature = PersonalMessage.sign(
  message: Text,
  privateKey: [Nat8]
);
// Returns: [Nat8]

// Create signed message object
let signedMessage = PersonalMessage.createSignedMessage(
  message: Text,
  signature: [Nat8],
  address: Text
);
// Returns: {
//   message: Text;
//   signature: [Nat8];
//   address: Text;
// }
```

### Verifying Messages

```motoko
// Verify signature
let isValid = PersonalMessage.verify(
  message: Text,
  signature: [Nat8],
  publicKey: [Nat8]
);
// Returns: Bool

// Verify signed message
let isValid = PersonalMessage.verifySignedMessage(
  signedMessage: SignedMessage
);
// Returns: Bool
```

## Complete Example

```motoko
import Wallet "mo:hoosat-mo/wallet";
import Address "mo:hoosat-mo/address";
import Validation "mo:hoosat-mo/validation";
import Errors "mo:hoosat-mo/errors";
import Types "mo:hoosat-mo/types";
import Debug "mo:base/Debug";
import Result "mo:base/Result";

actor HoosatWallet {
  // Create wallet instance
  let wallet = Wallet.createMainnetWallet("my-app", ?"hoosat");
  
  // Validate and get balance
  public func getBalance(address: Text) : async Text {
    // Validate address first
    switch (Validation.validateAddress(address)) {
      case (#err(error)) {
        return "Invalid address: " # Errors.errorToText(error);
      };
      case (#ok(())) {};
    };
    
    // Get balance
    let result = await wallet.getBalance(address);
    
    switch (result) {
      case (#ok(balance)) {
        let htn = balance / 100_000_000;  // Convert sompi to HTN
        let sompi = balance % 100_000_000;
        return debug_show(htn) # "." # debug_show(sompi) # " HTN";
      };
      case (#err(error)) {
        return "Error: " # Errors.errorToText(error);
      };
    };
  };
  
  // Send Hoosat with validation
  public func send(
    from: Text,
    to: Text,
    amount: Nat64
  ) : async Text {
    // Validate all inputs
    switch (Validation.validateAddress(from)) {
      case (#err(e)) { return "Invalid from address" };
      case (#ok(())) {};
    };
    
    switch (Validation.validateAddress(to)) {
      case (#err(e)) { return "Invalid to address" };
      case (#ok(())) {};
    };
    
    switch (Validation.validateAmount(amount)) {
      case (#err(e)) { return "Invalid amount" };
      case (#ok(())) {};
    };
    
    // Send transaction
    let result = await wallet.sendTransaction(from, to, amount, null, null);
    
    switch (result) {
      case (#ok(txId)) {
        return "Success! Transaction ID: " # txId;
      };
      case (#err(#InsufficientFunds(info))) {
        return "Insufficient funds. Need: " # debug_show(info.required) # 
               ", Have: " # debug_show(info.available);
      };
      case (#err(error)) {
        return "Error: " # Errors.errorToText(error);
      };
    };
  };
  
  // Generate new address
  public func generateAddress() : async Text {
    let address = Address.generate("mainnet", Address.SCHNORR);
    return address;
  };
};
```

## Constants

```motoko
// Address payload lengths
Address.SCHNORR_PAYLOAD_LEN  // 32 bytes
Address.ECDSA_PAYLOAD_LEN    // 33 bytes

// Transaction defaults
Transaction.DUST_THRESHOLD   // 1,000 sompi
Transaction.DEFAULT_VERSION  // 0
Transaction.DEFAULT_SEQUENCE // 0

// Network APIs
Wallet.MAINNET_API  // "https://api.network.hoosat.fi"
Wallet.TESTNET_API  // "https://api.testnet.hoosat.fi"

// Unit conversion
1 HTN = 100_000_000 sompi
```

## Best Practices

### 1. Always Validate Inputs

```motoko
switch (Validation.validateAddress(address)) {
  case (#ok(())) { /* proceed */ };
  case (#err(e)) { /* handle error */ };
};
```

### 2. Use Structured Error Handling

```motoko
switch (result) {
  case (#err(#InsufficientFunds(info))) {
    Debug.print("Need: " # debug_show(info.required));
    Debug.print("Have: " # debug_show(info.available));
  };
  case (#err(#NetworkError(msg))) {
    Debug.print("Network issue: " # msg);
  };
  case (#err(error)) {
    Debug.print(Errors.errorToText(error));
  };
  case (#ok(value)) { /* success */ };
};
```

### 3. Minimize HTTP Outcalls

HTTP outcalls are expensive (cycles). Cache results when possible:

```motoko
private var balanceCache : [(Text, (Nat64, Nat64))] = [];

public func getCachedBalance(addr: Text, ttl: Nat64) : async Nat64 {
  let now = Time.now();
  
  switch (Array.find(balanceCache, func((a, _)) : Bool { a == addr })) {
    case (?(_, (balance, timestamp))) {
      if (now - timestamp < ttl) {
        return balance;
      };
    };
    case (null) {};
  };
  
  // Fetch fresh balance
  let result = await wallet.getBalance(addr);
  
  switch (result) {
    case (#ok(balance)) {
      balanceCache := Array.append(balanceCache, [(addr, (balance, now))]);
      return balance;
    };
    case (#err(_)) { return 0; };
  };
};
```

### 4. Handle Dust Threshold

```motoko
let DUST = 1000; // 1,000 sompi minimum

if (changeAmount < DUST) {
  // Add to fee instead of creating change output
  fee += changeAmount;
} else {
  // Create change output
  builder.addChangeOutput(changeAddress);
};
```

## Links

- **Mops Package**: https://mops.one/hoosat-mo
- **GitHub**: https://github.com/Hoosat-Oy/Hoosat-mo
- **Developer Hub**: https://hub.hoosat.net/docs/hoosat-mo
- **Test Suite**: https://github.com/Hoosat-Oy/Hoosat-mo/tree/main/test
- **Internet Computer**: https://internetcomputer.org/
