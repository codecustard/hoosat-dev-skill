import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hoosat dApp',
  description: 'Hoosat blockchain dApp',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-50">{children}</body>
    </html>
  )
}
