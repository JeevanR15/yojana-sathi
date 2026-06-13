import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

// Inter loaded via next/font (self-hosted at build, no external request at runtime).
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata: Metadata = {
  title: "Yojana Sathi — Voice Welfare Finder",
  description:
    "Speak your situation in any Indian language and discover the government welfare schemes you qualify for.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body
        className={`${inter.variable} bg-background font-sans text-white antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
