import type { Metadata } from 'next'
import './globals.css'
import { Navbar } from '@/components/layout/Navbar'
import { SignalTicker } from '@/components/layout/SignalTicker'
import { Footer } from '@/components/layout/Footer'

export const metadata: Metadata = {
  title: { template: '%s | Georgetown Signal', default: "Georgetown Signal — Georgetown TX's Trusted Local Source" },
  description: 'Real recommendations from real community conversations. Find verified local service providers in Georgetown, TX.',
  metadataBase: new URL(process.env.NEXT_PUBLIC_SITE_URL ?? 'https://georgetownsignal.com'),
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <Navbar />
        <SignalTicker />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  )
}
