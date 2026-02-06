# Hoosat dApp Template

A Next.js-based dApp template for building Hoosat blockchain applications.

## Features

- Wallet connection using `hoosat-sdk-web`
- Balance fetching from Hoosat network
- Transaction building and submission
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
├── hooks/
│   └── useHoosatWallet.ts    # Wallet hook
├── globals.css
├── layout.tsx
└── page.tsx
```

## SDK Usage

This template uses `hoosat-sdk-web` for blockchain interactions:

- `HoosatWebClient` - REST API client
- `HoosatCrypto` - Key generation and signing
- `HoosatTxBuilder` - Transaction building
- `HoosatUtils` - Utilities and validation

## Customization

- Implement wallet adapter for browser extension support
- Add HRC20 token support
- Customize UI components
- Add more blockchain features

## Links

- [Hoosat SDK Web](https://www.npmjs.com/package/hoosat-sdk-web)
- [Developer Hub](https://hub.hoosat.net/)
- [GitHub](https://github.com/hoosatnetwork)
