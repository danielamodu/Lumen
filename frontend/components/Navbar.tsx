"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Cpu, Terminal, BookOpen, Layers, ArrowUpRight } from "lucide-react";

export const Navbar: React.FC = () => {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-50 w-full border-b border-border-subtle bg-canvas/85 backdrop-blur-lg">
      <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-4 sm:px-6 lg:px-8">
        {/* Brand Lockup */}
        <Link href="/" className="flex items-center gap-3 group">
          <div className="w-8 h-8 rounded-lg bg-surface-2 border border-border-muted flex items-center justify-center text-indigo-400 group-hover:border-indigo-400/60 group-hover:text-indigo-300 transition-all shadow-sm">
            <Cpu className="w-4 h-4" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-lg font-extrabold tracking-tight text-white">LUMEN</span>
            <span className="hidden sm:inline-block text-[10px] font-mono tracking-widest text-text-muted uppercase">
              / MEMORY LAYER
            </span>
          </div>
        </Link>

        {/* Navigation Links */}
        <nav className="hidden md:flex items-center gap-7 text-xs font-medium">
          <Link
            href="/#architecture"
            className="text-text-secondary hover:text-white transition-colors flex items-center gap-1.5"
          >
            <Layers className="w-3.5 h-3.5 text-text-muted" />
            Architecture
          </Link>
          <Link
            href="/#features"
            className="text-text-secondary hover:text-white transition-colors"
          >
            Cross-Domain
          </Link>
          <Link
            href="/docs"
            className={`transition-colors flex items-center gap-1.5 ${
              pathname.startsWith("/docs")
                ? "text-white font-semibold"
                : "text-text-secondary hover:text-white"
            }`}
          >
            <BookOpen className="w-3.5 h-3.5 text-text-muted" />
            Documentation
          </Link>
          <Link
            href="/app"
            className={`transition-colors flex items-center gap-1.5 ${
              pathname === "/app"
                ? "text-indigo-400 font-semibold"
                : "text-text-secondary hover:text-white"
            }`}
          >
            <Terminal className="w-3.5 h-3.5 text-indigo-400" />
            Live Console
          </Link>
        </nav>

        {/* Right CTA Actions */}
        <div className="flex items-center gap-3">
          <Link
            href="/docs"
            className="hidden sm:inline-flex items-center gap-1 text-xs font-mono text-text-secondary hover:text-white px-3 py-1.5 rounded-lg border border-border-subtle hover:border-border-muted transition-colors"
          >
            <span>v1.0 SDK</span>
            <ArrowUpRight className="w-3 h-3 text-text-muted" />
          </Link>
          <Link
            href="/app"
            className="inline-flex items-center gap-1.5 bg-brand-500 hover:bg-brand-600 text-white text-xs font-semibold px-4 py-2 rounded-lg transition-all shadow-glow hover:brightness-110 active:scale-[0.98]"
          >
            <Terminal className="w-3.5 h-3.5" />
            <span>Launch Console</span>
          </Link>
        </div>
      </div>
    </header>
  );
};
