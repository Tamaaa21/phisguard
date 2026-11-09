import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PhishGuard — Detektor Link Phishing Berbasis AI & Machine Learning",
  description:
    "Periksa apakah sebuah tautan aman atau phishing menggunakan model Machine Learning pada 49 fitur URL string tanpa membuka situs target (Zero-SSRF).",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="id" className="scroll-smooth">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="font-sans antialiased bg-[#090d16] text-slate-100 min-h-screen flex flex-col selection:bg-sky-500/30 selection:text-sky-200">
        {children}
      </body>
    </html>
  );
}
