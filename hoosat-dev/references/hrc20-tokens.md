# HRC20 Token Standard

HRC20 is Hoosat's token standard, equivalent to Kaspa's KRC20, enabling fungible tokens on the Hoosat blockchain.

## Overview

HRC20 tokens are built on top of Hoosat's transaction layer, utilizing the payload field for token metadata and operations.

**Key Features:**
- Fungible token creation and management
- Standardized transfer and approval mechanisms
- Compatible with existing wallet infrastructure
- Low transaction fees

## Status

**HRC20 is currently in development.** The standard follows Kasplex KRC20 specification with Hoosat-specific adaptations.

## Token Structure

### Token Deployment

```json
{
  "p": "hrc-20",
  "op": "deploy",
  "tick": "TOKEN",
  "max": "21000000",
  "lim": "1000",
  "dec": "8",
  "pre": "1000000"
}
```

**Fields:**
- `p`: Protocol identifier ("hrc-20")
- `op`: Operation type ("deploy", "mint", "transfer")
- `tick`: Token ticker symbol (4-5 characters)
- `max`: Maximum supply
- `lim`: Mint limit per transaction
- `dec`: Decimal places (0-18)
- `pre`: Pre-mint amount (optional)

### Token Minting

```json
{
  "p": "hrc-20",
  "op": "mint",
  "tick": "TOKEN",
  "amt": "1000"
}
```

### Token Transfer

```json
{
  "p": "hrc-20",
  "op": "transfer",
  "tick": "TOKEN",
  "amt": "500",
  "to": "hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe"
}
```

## Implementation (Future)

### JavaScript/TypeScript SDK Integration

```typescript
import { HoosatClient, HoosatUtils } from 'hoosat-sdk';

// Deploy token (when available)
async function deployToken(
  client: HoosatClient,
  wallet: KeyPair,
  params: {
    ticker: string;
    maxSupply: string;
    mintLimit: string;
    decimals: number;
  }
) {
  const deployPayload = JSON.stringify({
    p: 'hrc-20',
    op: 'deploy',
    tick: params.ticker,
    max: params.maxSupply,
    lim: params.mintLimit,
    dec: params.decimals
  });
  
  // Transaction with token payload
  const tx = await buildTransaction({
    ...transactionParams,
    payload: deployPayload
  });
  
  return client.submitTransaction(tx);
}

// Mint tokens (when available)
async function mintTokens(
  client: HoosatClient,
  wallet: KeyPair,
  ticker: string,
  amount: string
) {
  const mintPayload = JSON.stringify({
    p: 'hrc-20',
    op: 'mint',
    tick: ticker,
    amt: amount
  });
  
  const tx = await buildTransaction({
    ...transactionParams,
    payload: mintPayload
  });
  
  return client.submitTransaction(tx);
}

// Transfer tokens (when available)
async function transferTokens(
  client: HoosatClient,
  wallet: KeyPair,
  ticker: string,
  amount: string,
  recipient: string
) {
  const transferPayload = JSON.stringify({
    p: 'hrc-20',
    op: 'transfer',
    tick: ticker,
    amt: amount,
    to: recipient
  });
  
  const tx = await buildTransaction({
    ...transactionParams,
    payload: transferPayload
  });
  
  return client.submitTransaction(tx);
}
```

### Motoko Integration (Future)

```motoko
import Token "mo:hoosat-mo/token";

// Deploy token
let deployResult = await Token.deploy({
  ticker = "TOKEN";
  maxSupply = 21_000_000;
  decimals = 8;
});

// Mint tokens
let mintResult = await Token.mint("TOKEN", 1000);

// Transfer tokens
let transferResult = await Token.transfer(
  "TOKEN",
  "hoosat:recipient...",
  500
);
```

## Token Indexer (Future)

To track HRC20 token balances and transactions, an indexer service will be required:

```typescript
// Example indexer API
interface HRC20Indexer {
  getBalance(address: string, ticker: string): Promise<string>;
  getTokenInfo(ticker: string): Promise<TokenInfo>;
  getTransfers(ticker: string, address?: string): Promise<Transfer[]>;
  getHolders(ticker: string): Promise<Holder[]>;
}

// Usage
const indexer = new HRC20Indexer('https://api.hoosat.net/hrc20');

const balance = await indexer.getBalance(
  'hoosat:qz7ulu8mmmul6hdcnssmjnt28h2xfer8dz9nfqamvvh86ngef4q8dvzxcjdqe',
  'TOKEN'
);
```

## Token Metadata

### Standard Metadata

```json
{
  "ticker": "TOKEN",
  "name": "Token Name",
  "description": "Token description",
  "image": "https://example.com/token.png",
  "decimals": 8,
  "maxSupply": "21000000",
  "totalMinted": "5000000",
  "holders": 1234,
  "transactions": 5678
}
```

## Wallet Integration (Future)

### Displaying Token Balances

```typescript
// Wallet UI integration
interface TokenBalance {
  ticker: string;
  name: string;
  balance: string;
  balanceHtn: string;  // Value in HTN if available
  decimals: number;
  icon?: string;
}

// Fetch all token balances for address
async function getTokenBalances(address: string): Promise<TokenBalance[]> {
  // Implementation will depend on indexer availability
  const response = await fetch(
    `https://api.hoosat.net/hrc20/balances/${address}`
  );
  return response.json();
}
```

### Token Transfer UI

```typescript
// Token transfer component
interface TokenTransferProps {
  token: TokenBalance;
  onTransfer: (recipient: string, amount: string) => Promise<void>;
}

function TokenTransfer({ token, onTransfer }: TokenTransferProps) {
  const [recipient, setRecipient] = useState('');
  const [amount, setAmount] = useState('');
  
  const handleSubmit = async () => {
    await onTransfer(recipient, amount);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Recipient address (hoosat:...)"
        value={recipient}
        onChange={e => setRecipient(e.target.value)}
      />
      <input
        placeholder={`Amount (${token.ticker})`}
        value={amount}
        onChange={e => setAmount(e.target.value)}
      />
      <button type="submit">Transfer</button>
    </form>
  );
}
```

## Security Considerations

### Token Validation

```typescript
// Validate ticker
function isValidTicker(ticker: string): boolean {
  // Ticker must be 4-5 uppercase letters/numbers
  return /^[A-Z0-9]{4,5}$/.test(ticker);
}

// Validate amount
function isValidAmount(amount: string, decimals: number): boolean {
  const regex = new RegExp(`^\\d+(\\.\\d{1,${decimals}})?$`);
  return regex.test(amount);
}

// Validate HRC20 payload
function validateHrc20Payload(payload: any): boolean {
  if (typeof payload !== 'object') return false;
  if (payload.p !== 'hrc-20') return false;
  if (!['deploy', 'mint', 'transfer'].includes(payload.op)) return false;
  if (!isValidTicker(payload.tick)) return false;
  
  return true;
}
```

### Preventing Double Spend

Token transfers must be processed atomically with Hoosat's consensus:

1. Include token payload in transaction
2. Wait for transaction confirmation
3. Verify via indexer
4. Update UI only after confirmation

## Comparison with ERC20

| Feature | ERC20 (Ethereum) | HRC20 (Hoosat) |
|---------|------------------|----------------|
| **Gas Fees** | Variable (ETH) | Fixed (HTN) |
| **Confirmation Time** | ~12 seconds | ~1 second |
| **Scalability** | Limited | High (BlockDAG) |
| **Smart Contracts** | Required | Not required |
| **Token Logic** | On-chain | Transaction metadata |

## Development Timeline

- **Phase 1**: Standard specification (In Progress)
- **Phase 2**: Indexer development
- **Phase 3**: SDK integration
- **Phase 4**: Wallet support
- **Phase 5**: Mainnet launch

## Testing (Testnet)

When HRC20 is available on testnet:

```bash
# Get testnet HTN from faucet
curl https://faucet.hoosat.net/request \
  -d '{"address": "hoosattest:your-address"}'

# Deploy test token
# Use SDK or raw transaction with testnet payload
```

## Resources

- **Kasplex KRC20**: https://docs.kasplex.org/ (reference implementation)
- **Hoosat GitHub**: https://github.com/hoosatnetwork
- **Developer Hub**: https://hub.hoosat.net/

## Notes

- HRC20 is currently in development
- Specifications may change before mainnet launch
- Follow official Hoosat channels for updates
- Test thoroughly on testnet before mainnet deployment
