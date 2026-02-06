import { useState, useEffect, useCallback } from 'react'
import {
  HoosatWebClient,
  HoosatCrypto,
  HoosatTxBuilder,
  HoosatUtils,
  HoosatSigner
} from 'hoosat-sdk-web'

export function useHoosatWallet() {
  const [client] = useState(() => new HoosatWebClient({
    baseUrl: 'https://proxy.hoosat.net/api/v1'
  }))
  const [wallet, setWallet] = useState<{
    address: string
    publicKey: Buffer
    privateKey: Buffer
  } | null>(null)
  const [balance, setBalance] = useState<string>('0')
  const [loading, setLoading] = useState(false)

  const connected = wallet !== null

  const connect = useCallback(async () => {
    setLoading(true)
    try {
      // Generate new wallet for demo
      // In production, use wallet adapter or import from extension
      const newWallet = HoosatCrypto.generateKeyPair('mainnet')
      setWallet(newWallet)
      
      // Fetch balance
      const bal = await client.getBalance(newWallet.address)
      setBalance(HoosatUtils.sompiToAmount(bal))
    } finally {
      setLoading(false)
    }
  }, [client])

  const disconnect = useCallback(() => {
    setWallet(null)
    setBalance('0')
  }, [])

  const refreshBalance = useCallback(async () => {
    if (wallet) {
      const bal = await client.getBalance(wallet.address)
      setBalance(HoosatUtils.sompiToAmount(bal))
    }
  }, [client, wallet])

  const send = useCallback(async (recipient: string, amountHtn: string) => {
    if (!wallet) throw new Error('Wallet not connected')

    // Validate address
    if (!HoosatUtils.isValidAddress(recipient)) {
      throw new Error('Invalid recipient address')
    }

    // Get UTXOs
    const utxos = await client.getUtxos([wallet.address])

    // Get fee estimate
    const feeEstimate = await client.getFeeEstimate()
    const fee = feeEstimate.normalBucket.feeRate.toString()

    // Build transaction
    const builder = new HoosatTxBuilder()
    utxos.forEach(utxo => builder.addInput(utxo, wallet.privateKey))

    builder
      .addOutput(recipient, HoosatUtils.amountToSompi(amountHtn))
      .setFee(fee)
      .addChangeOutput(wallet.address)

    // Sign and submit
    const signedTx = builder.sign()
    const txId = await client.submitTransaction(signedTx)

    // Refresh balance
    await refreshBalance()

    return txId
  }, [client, wallet, refreshBalance])

  // Poll balance every 30 seconds
  useEffect(() => {
    if (!wallet) return

    const interval = setInterval(refreshBalance, 30000)
    return () => clearInterval(interval)
  }, [wallet, refreshBalance])

  return {
    address: wallet?.address || null,
    balance,
    connected,
    loading,
    connect,
    disconnect,
    send,
    refreshBalance
  }
}
