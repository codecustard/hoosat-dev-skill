# Hoosat Block Explorer Template

A Next.js-based block explorer template for the Hoosat blockchain.

## Features

- Real-time network stats
- Block and transaction search
- Address balance lookup
- Built with TypeScript and Tailwind CSS

## Getting Started

1. Install dependencies:
```bash
npm install
```

2. Run development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000)

## Project Structure

```
app/
├── lib/
│   └── api.ts              # API client
├── globals.css
├── layout.tsx
└── page.tsx
```

## SDK Usage

This template uses `hoosat-sdk-web` for blockchain data:

- `HoosatWebClient` - REST API client
- `getNodeInfo()` - Network status
- `getBlueScore()` - Current block height
- `getBlock()` - Block details
- `getBalance()` - Address balance

## Customization

- Add block list pagination
- Implement transaction details view
- Add address transaction history
- Customize UI theme

## Links

- [Hoosat SDK Web](https://www.npmjs.com/package/hoosat-sdk-web)
- [Developer Hub](https://hub.hoosat.net/)
- [GitHub](https://github.com/hoosatnetwork)
