# Hoosat REST API Reference

Complete reference for the Hoosat REST API at `https://proxy.hoosat.net/api/v1`.

## Base URL

```
Production: https://proxy.hoosat.net/api/v1
Local Development: http://localhost:3000/api/v1
```

## Response Format

All endpoints return standardized responses:

### Success Response
```json
{
  "success": true,
  "data": { ... },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/node/info"
}
```

### Error Response
```json
{
  "success": false,
  "error": "Error message description",
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/node/info"
}
```

## Authentication

Currently, the API does not require authentication. All endpoints are publicly accessible.

## Rate Limiting

No rate limiting is currently enforced.

## Error Handling

HTTP Status Codes:
- **200** - Success
- **400** - Bad Request (invalid parameters)
- **404** - Not Found
- **500** - Internal Server Error

## Interactive Documentation

Full interactive API documentation available at:
**https://proxy.hoosat.net/docs**

---

## Node Endpoints

### Get Node Info

Retrieve node information and status.

**Endpoint:** `GET /node/info`

**Response:**
```json
{
  "success": true,
  "data": {
    "p2pId": "a2bb90a5d6c686ebc5d933e157a28263",
    "mempoolSize": "45",
    "serverVersion": "0.1.0",
    "isUtxoIndexed": true,
    "isSynced": true
  },
  "timestamp": 1760025889814,
  "path": "/api/v1/node/info"
}
```

### Get Blue Score

Get the current blockchain height (blue score).

**Endpoint:** `GET /node/blue-score`

**Response:**
```json
{
  "success": true,
  "data": {
    "blueScore": "12345678"
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/node/blue-score"
}
```

### Get Coin Supply

Get current circulating and max supply.

**Endpoint:** `GET /node/coin-supply`

**Response:**
```json
{
  "success": true,
  "data": {
    "circulatingSupply": "23000000000000000",
    "maxSupply": "28700000000000000"
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/node/coin-supply"
}
```

### Estimate Network Hashrate

Get estimated network hashrate.

**Endpoint:** `GET /node/estimate-hashrate`

**Response:**
```json
{
  "success": true,
  "data": {
    "networkHashesPerSecond": "12345678901234567890"
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/node/estimate-hashrate"
}
```

### Health Check

Check node health status.

**Endpoint:** `GET /node/health`

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy"
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/node/health"
}
```

---

## Blockchain Endpoints

### Get Tip Hash

Get the hash of the latest block.

**Endpoint:** `GET /blockchain/tip-hash`

**Response:**
```json
{
  "success": true,
  "data": {
    "tipHash": "abcd1234..."
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/blockchain/tip-hash"
}
```

### Get Block

Get a block by its hash.

**Endpoint:** `GET /blockchain/block/:hash`

**Response:**
```json
{
  "success": true,
  "data": {
    "hash": "abcd1234...",
    "version": 0,
    "hashMerkleRoot": "efgh5678...",
    "acceptedIdMerkleRoot": "ijkl9012...",
    "utxoCommitment": "mnop3456...",
    "timestamp": 1704067200000,
    "bits": 486604799,
    "nonce": 1234567890,
    "daaScore": 12345678,
    "blueScore": 12345678,
    "blueWork": "1234567890abcdef",
    "pruningPoint": "qrst7890...",
    "transactions": [...]
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/blockchain/block/:hash"
}
```

### Get Blocks

Get multiple blocks starting from a low hash.

**Endpoint:** `GET /blockchain/blocks/:lowHash`

**Response:**
```json
{
  "success": true,
  "data": {
    "blocks": [...]
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/blockchain/blocks/:lowHash"
}
```

### Get Block Count

Get the total block count.

**Endpoint:** `GET /blockchain/count`

### Get DAG Info

Get DAG (Directed Acyclic Graph) information.

**Endpoint:** `GET /blockchain/dag-info`

---

## Address Endpoints

### Get Balance

Get balance for a single address.

**Endpoint:** `GET /address/:address/balance`

**Response:**
```json
{
  "success": true,
  "data": {
    "balance": "1000000000"
  },
  "timestamp": 1760026085383,
  "path": "/api/v1/address/:address/balance"
}
```

**Example:**
```bash
curl https://proxy.hoosat.net/api/v1/address/hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe/balance
```

### Get Balances (Batch)

Get balances for multiple addresses.

**Endpoint:** `POST /address/balances`

**Request Body:**
```json
{
  "addresses": [
    "hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe",
    "hoosat:qqkqkzjvr7zwxxmjxjkmxx"
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "balances": [
      {
        "address": "hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe",
        "balance": "1000000000"
      }
    ]
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/address/balances"
}
```

### Get UTXOs

Get UTXOs for addresses.

**Endpoint:** `POST /address/utxos`

**Request Body:**
```json
{
  "addresses": ["hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "utxos": [
      {
        "address": "hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe",
        "outpoint": {
          "transactionId": "abcd1234...",
          "index": 0
        },
        "utxoEntry": {
          "amount": "1000000000",
          "scriptPublicKey": {
            "scriptPublicKey": "76a914...",
            "version": 0
          },
          "blockDaaScore": "12345678",
          "isCoinbase": false
        }
      }
    ]
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/address/utxos"
}
```

---

## Network Endpoints

### Get Network Info

Get current network information.

**Endpoint:** `GET /network/info`

**Response:**
```json
{
  "success": true,
  "data": {
    "network": "mainnet"
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/network/info"
}
```

### Get Peers

Get list of peer addresses.

**Endpoint:** `GET /network/peers`

### Get Connected Peers

Get detailed information about connected peers.

**Endpoint:** `GET /network/connected-peers`

---

## Mempool Endpoints

### Get Mempool Entry

Get a specific transaction from the mempool.

**Endpoint:** `GET /mempool/entry/:txId`

### Get All Mempool Entries

Get all mempool entries.

**Endpoint:** `GET /mempool/entries`

### Get Mempool Entries by Addresses

Get mempool entries filtered by addresses.

**Endpoint:** `POST /mempool/entries-by-addresses`

**Request Body:**
```json
{
  "addresses": ["hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"]
}
```

### Get Fee Estimate

Get fee estimation for transaction priority.

**Endpoint:** `GET /mempool/fee-estimate`

**Response:**
```json
{
  "success": true,
  "data": {
    "priorityBucket": {
      "feeRate": 1000,
      "estimatedSeconds": 1
    },
    "normalBucket": {
      "feeRate": 100,
      "estimatedSeconds": 10
    },
    "lowBucket": {
      "feeRate": 10,
      "estimatedSeconds": 60
    }
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/mempool/fee-estimate"
}
```

---

## Transaction Endpoints

### Submit Transaction

Submit a signed transaction to the network.

**Endpoint:** `POST /transaction/submit`

**Request Body:**
```json
{
  "version": 0,
  "inputs": [
    {
      "previousOutpoint": {
        "transactionId": "abcd1234...",
        "index": 0
      },
      "signatureScript": "483045022100...",
      "sequence": 0,
      "sigOpCount": 1
    }
  ],
  "outputs": [
    {
      "amount": "900000000",
      "scriptPublicKey": {
        "scriptPublicKey": "76a914...",
        "version": 0
      }
    }
  ],
  "lockTime": "0",
  "subnetworkId": "0000000000000000000000000000000000000000",
  "gas": "0",
  "payload": ""
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "transactionId": "efgh5678..."
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/transaction/submit"
}
```

### Get Transaction Status

Get the status of a transaction.

**Endpoint:** `GET /transaction/:txId/status`

**Response:**
```json
{
  "success": true,
  "data": {
    "transactionId": "abcd1234...",
    "status": "accepted",
    "confirmingBlockHash": "efgh5678...",
    "confirmingBlockBlueScore": 12345678
  },
  "timestamp": "2025-01-10T12:00:00.000Z",
  "path": "/api/v1/transaction/:txId/status"
}
```

---

## Code Examples

### JavaScript/TypeScript

```typescript
import axios from 'axios';

const client = axios.create({
  baseURL: 'https://proxy.hoosat.net/api/v1'
});

// Get balance
const getBalance = async (address: string) => {
  const response = await client.get(`/address/${address}/balance`);
  return response.data.data.balance;
};

// Submit transaction
const submitTransaction = async (tx: any) => {
  const response = await client.post('/transaction/submit', tx);
  return response.data.data.transactionId;
};
```

### Python

```python
import requests

BASE_URL = 'https://proxy.hoosat.net/api/v1'

# Get balance
def get_balance(address):
    response = requests.get(f'{BASE_URL}/address/{address}/balance')
    return response.json()['data']['balance']

# Get UTXOs
def get_utxos(addresses):
    response = requests.post(
        f'{BASE_URL}/address/utxos',
        json={'addresses': addresses}
    )
    return response.json()['data']['utxos']
```

### cURL

```bash
# Get node info
curl https://proxy.hoosat.net/api/v1/node/info

# Get address balance
curl https://proxy.hoosat.net/api/v1/address/hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe/balance

# Submit transaction
curl -X POST https://proxy.hoosat.net/api/v1/transaction/submit \
  -H "Content-Type: application/json" \
  -d '{
    "version": 0,
    "inputs": [...],
    "outputs": [...],
    "lockTime": "0",
    "subnetworkId": "0000000000000000000000000000000000000000",
    "gas": "0",
    "payload": ""
  }'
```

---

## Data Types

### Address

Hoosat addresses use Bech32 encoding:
- Mainnet: `hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe`
- Testnet: `hoosattest:qqkqkzjvr7zwxxmjxjkmxx`

### Amount

Amounts are represented as strings in sompi (1 HTN = 100,000,000 sompi).

### Transaction

```typescript
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

### UTXO

```typescript
interface UtxoEntry {
  address: string;
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
```

## Links

- **Live API**: https://proxy.hoosat.net/api/v1
- **Swagger Docs**: https://proxy.hoosat.net/docs
- **GitHub (Proxy)**: https://github.com/Namp88/hoosat-proxy
- **NPM Package**: https://www.npmjs.com/package/hoosat-proxy
