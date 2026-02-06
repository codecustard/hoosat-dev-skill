import { HoosatWebClient } from 'hoosat-sdk-web'

const client = new HoosatWebClient({
  baseUrl: 'https://proxy.hoosat.net/api/v1'
})

export async function getBlock(hash: string) {
  return client.getBlock(hash)
}

export async function getTransaction(txId: string) {
  return client.getTransactionStatus(txId)
}

export async function getAddressBalance(address: string) {
  return client.getBalance(address)
}

export async function getAddressUtxos(address: string) {
  return client.getUtxos([address])
}

export { client }
