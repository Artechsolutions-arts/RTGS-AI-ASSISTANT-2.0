import type { Metadata } from 'next'
import { Noto_Sans, Sree_Krushnadevaraya } from 'next/font/google'
import './globals.css'

const notoSans = Noto_Sans({ 
  subsets: ['latin'],
  weight: ['400', '500', '700', '900'],
  variable: '--font-noto-sans',
})

const sreeKrushnadevaraya = Sree_Krushnadevaraya({
  weight: '400',
  subsets: ['telugu'],
  variable: '--font-telugu',
})

export const metadata: Metadata = {
  title: 'Andhra Pradesh Government Dashboard',
  description: 'Official dashboard for Andhra Pradesh Government districts',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={`${notoSans.variable} ${sreeKrushnadevaraya.variable}`}>
      <body className="antialiased">{children}</body>
    </html>
  )
}
