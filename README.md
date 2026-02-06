# Hoosat Dev Skill

Comprehensive Hoosat blockchain development toolkit for AI Agents.

## Overview

This skill provides comprehensive support for Hoosat blockchain development. Hoosat is a Kaspa fork that uses BLAKE3 and Hoohash consensus algorithms with HTN as its native token.

**Key Characteristics:**
- **Ticker**: HTN
- **Address Prefix**: `hoosat:` (mainnet), `hoosattest:` (testnet)
- **Consensus**: BLAKE3 and Hoohash
- **SDKs**: hoosat-sdk (Node.js), hoosat-sdk-web (Browser), hoosat-mo (Motoko/IC)
- **API**: https://proxy.hoosat.net/api/v1

## Installation

### Option 1: Using npx skills (Recommended)
```bash
npx skills add codecustard/hoosat-dev-skill
```

### Option 2: Manual Installation
1. Download `hoosat-dev.skill` from releases
2. Copy to your skills directory

### Option 3: Build from Source
1. Clone this repository
2. Package the skill using skill-creator scripts

## Contents

```
hoosat-dev/
├── SKILL.md                          # Main skill documentation
├── references/
│   ├── api-reference.md              # REST API documentation
│   ├── hoosat-sdk.md                 # Node.js SDK docs
│   ├── hoosat-sdk-web.md             # Browser SDK docs
│   ├── hoosat-mo.md                  # Motoko/IC SDK docs
│   ├── wallet-integration.md         # Wallet integration guide
│   ├── node-operations.md            # Node setup guide
│   └── hrc20-tokens.md               # HRC20 token standard
├── scripts/
│   ├── generate-address.py           # Address generator
│   └── build-transaction.py          # Transaction builder
└── assets/
    ├── dapp-template/                # Next.js dApp starter
    └── explorer-template/            # Block explorer starter
```

## Quick Start

### Generate Address
```bash
python hoosat-dev/scripts/generate-address.py --network mainnet
```

### Install SDK
```bash
npm install hoosat-sdk-web
```

### Use in Code
```typescript
import { HoosatCrypto } from 'hoosat-sdk-web';

const wallet = HoosatCrypto.generateKeyPair('mainnet');
console.log('Address:', wallet.address);
```

## Documentation

- **Developer Hub**: https://hub.hoosat.net/
- **REST API Docs**: https://proxy.hoosat.net/docs
- **GitHub (Network)**: https://github.com/hoosatnetwork
- **Motoko Package**: https://mops.one/hoosat-mo

## License

MIT License - see LICENSE file

## Contributing

Contributions welcome!
