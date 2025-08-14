import './globals.css'

export const metadata = {
  title: 'ADHD Chore Chart',
  description: 'Interactive chore management with voice guidance',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
