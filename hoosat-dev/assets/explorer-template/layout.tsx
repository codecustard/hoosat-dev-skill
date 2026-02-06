import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Hoosat Explorer',
  description: 'Hoosat blockchain explorer',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-gray-900 text-white">{children}</body>
    </html>
  )
}
