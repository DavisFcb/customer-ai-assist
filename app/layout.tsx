import './globals.css';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'LibertyAI Assist',
  description: 'WhatsApp-style insurance support interface',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
