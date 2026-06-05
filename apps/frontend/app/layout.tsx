import type { Metadata } from "next";
import { Inter, Outfit } from "next/font/google";
import "./globals.css";
import { cn } from "@/lib/utils";

const inter = Inter({ subsets: ["latin"], variable: "--font-sans" });
const outfit = Outfit({ subsets: ["latin"], variable: "--font-display" });

export const metadata: Metadata = {
  title: "AI Success Coach - Dallas College",
  description: "Navigate your academic journey, evaluate course plans, track financial aid, and get immediate catalog answers with your AI Success Coach.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={cn(
        "h-full",
        "antialiased",
        "dark",
        inter.variable,
        outfit.variable,
        "font-sans"
      )}
    >
      <body className="min-h-full flex flex-col bg-[#030712] text-zinc-50">{children}</body>
    </html>
  );
}
