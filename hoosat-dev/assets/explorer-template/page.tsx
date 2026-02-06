'use client'

import { useState, useEffect } from 'react'
import { HoosatWebClient } from 'hoosat-sdk-web'

export default function Home() {
  const [client] = useState(() => new HoosatWebClient({
    baseUrl: 'https://proxy.hoosat.net/api/v1'
  }))
  const [nodeInfo, setNodeInfo] = useState<any>(null)
  const [blueScore, setBlueScore] = useState<string>('0')

  useEffect(() => {
    const fetchData = async () => {
      const info = await client.getNodeInfo()
      const score = await client.getBlueScore()
      setNodeInfo(info)
      setBlueScore(score)
    }
    fetchData()
    const interval = setInterval(fetchData, 30000)
    return () => clearInterval(interval)
  }, [client])

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">Hoosat Explorer</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-400">Blue Score</h2>
            <p className="text-3xl font-bold">{parseInt(blueScore).toLocaleString()}</p>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-400">Mempool Size</h2>
            <p className="text-3xl font-bold">{nodeInfo?.mempoolSize || '0'}</p>
          </div>
          
          <div className="bg-gray-800 p-6 rounded-lg">
            <h2 className="text-lg font-semibold text-gray-400">Synced</h2>
            <p className="text-3xl font-bold">{nodeInfo?.isSynced ? 'Yes' : 'No'}</p>
          </div>
        </div>

        <div className="bg-gray-800 p-6 rounded-lg mb-8">
          <h2 className="text-2xl font-semibold mb-4">Search</h2>
          <SearchBar />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <RecentBlocks client={client} />
          <NetworkStats nodeInfo={nodeInfo} />
        </div>
      </div>
    </main>
  )
}

function SearchBar() {
  const [query, setQuery] = useState('')

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    // Implement search logic
    console.log('Searching:', query)
  }

  return (
    <form onSubmit={handleSearch} className="flex gap-4">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder="Search by address, transaction, or block..."
        className="flex-1 p-3 bg-gray-700 rounded text-white placeholder-gray-400"
      />
      <button
        type="submit"
        className="px-6 py-3 bg-blue-500 hover:bg-blue-600 rounded font-semibold"
      >
        Search
      </button>
    </form>
  )
}

function RecentBlocks({ client }: { client: HoosatWebClient }) {
  const [blocks, setBlocks] = useState<any[]>([])

  useEffect(() => {
    const fetchBlocks = async () => {
      // This would fetch recent blocks from the API
      // Implementation depends on available endpoints
    }
    fetchBlocks()
  }, [client])

  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-2xl font-semibold mb-4">Recent Blocks</h2>
      <div className="space-y-4">
        <p className="text-gray-400">Block data will be displayed here</p>
        {/* Implement block list */}
      </div>
    </div>
  )
}

function NetworkStats({ nodeInfo }: { nodeInfo: any }) {
  return (
    <div className="bg-gray-800 p-6 rounded-lg">
      <h2 className="text-2xl font-semibold mb-4">Network Stats</h2>
      <div className="space-y-3">
        <div className="flex justify-between">
          <span className="text-gray-400">Server Version</span>
          <span>{nodeInfo?.serverVersion || 'Unknown'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">P2P ID</span>
          <span className="truncate max-w-xs">{nodeInfo?.p2pId || 'Unknown'}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-400">UTXO Indexed</span>
          <span>{nodeInfo?.isUtxoIndexed ? 'Yes' : 'No'}</span>
        </div>
      </div>
    </div>
  )
}
