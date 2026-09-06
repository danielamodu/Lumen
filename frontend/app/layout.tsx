import type { Metadata } from "next";
import Script from "next/script";
import "./globals.css";

export const dynamic = "force-dynamic";

export const metadata: Metadata = {
  title: "Lumen — Architectural Memory for Agents",
  description:
    "The outcome memory layer that makes any agent learn from experience. Not fine-tuning. Not RAG. Just memory.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className="min-h-screen bg-[#0C0A09] text-[#E7E5E4] font-sans antialiased selection:bg-lime-400/20 selection:text-lime-300">
        <Script
          src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"
          strategy="beforeInteractive"
        />
        {children}
      </body>
    </html>
  );
}
