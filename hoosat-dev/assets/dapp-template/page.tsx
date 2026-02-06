'use client'

import { useHoosatWallet } from './hooks/useHoosatWallet'

export default function Home() {
  const { address, balance, connected, loading, connect, disconnect, send } = useHoosatWallet()

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Hoosat dApp Template</h1>
        
        <div className="bg-gray-100 p-6 rounded-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4">Wallet Connection</h2>
          
          {!connected ? (
            <button
              onClick={connect}
              disabled={loading}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
            >
              {loading ? 'Connecting...' : 'Connect Wallet'}
            </button>
          ) : (
            <div>
              <p className="mb-2">
                <span className="font-semibold">Address:</span> {address}
              </p>
              <p className="mb-4">
                <span className="font-semibold">Balance:</span>{' '}
                {balance ? `${balance} HTN` : 'Loading...'}
              </p>
              <button
                onClick={disconnect}
                className="bg-red-500 hover:bg-red-600 text-white font-bold py-2 px-4 rounded"
              >
                Disconnect
              </button>
            </div>
          )}
        </div>

        <div className="bg-gray-100 p-6 rounded-lg">
          <h2 className="text-2xl font-semibold mb-4">Features</h2>
          <ul className="list-disc list-inside space-y-2">
            <li>Wallet connection via hoosat-sdk-web</li>
            <li>Balance fetching from Hoosat network</li>
            <li>Transaction building (implement in hooks/useHoosatWallet.ts)</li>
            <li>HRC20 token support (implement as needed)</li>
          </ul>
        </div>

        {connected && (
          <div className="bg-gray-100 p-6 rounded-lg mt-8">
            <h2 className="text-2xl font-semibold mb-4">Send HTN</h2>
            <SendForm onSend={send} />
          </div>
        )}
      </div>
    </main>
  )
}

function SendForm({ onSend }: { onSend: (recipient: string, amount: string) => Promise<void> }) {
  const [recipient, setRecipient] = useState('')
  const [amount, setAmount] = useState('')
  const [sending, setSending] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSending(true)
    try {
      await onSend(recipient, amount)
      setRecipient('')
      setAmount('')
    } finally {
      setSending(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="block text-sm font-medium mb-1">Recipient Address</label>
        <input
          type="text"
          value={recipient}
          onChange={(e) => setRecipient(e.target.value)}
          placeholder="hoosat:..."
          className="w-full p-2 border rounded"
          required
        />
      </div>
      <div>
        <label className="block text-sm font-medium mb-1">Amount (HTN)</label>
        <input
          type="number"
          step="0.00000001"
          value={amount}
          onChange={(e) => setAmount(e.target.value)}
          placeholder="0.00"
          className="w-full p-2 border rounded"
          required
        />
      </div>
      <button
        type="submit"
        disabled={sending}
        className="bg-green-500 hover:bg-green-600 text-white font-bold py-2 px-4 rounded disabled:opacity-50"
      >
        {sending ? 'Sending...' : 'Send'}
      </button>
    </form>
  )
}

import { useState } from 'react'
