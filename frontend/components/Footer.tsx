import React from "react";
import Link from "next/link";
import { Cpu, ShieldCheck, ArrowUpRight } from "lucide-react";

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-border-subtle bg-canvas text-text-secondary mt-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-10">
          {/* Brand Column */}
          <div className="space-y-4 md:col-span-1">
            <div className="flex items-center gap-2.5">
              <div className="w-7 h-7 rounded-lg bg-surface-2 border border-border-muted flex items-center justify-center text-indigo-400">
                <Cpu className="w-3.5 h-3.5" />
              </div>
              <span className="text-base font-extrabold text-white tracking-tight">LUMEN</span>
            </div>
            <p className="text-xs text-text-muted leading-relaxed">
              Outcome memory substrate for autonomous AI agents. Empowering stateless reasoning models to compound competence over time.
            </p>
            <div className="flex items-center gap-2 text-[11px] text-emerald-400/90 font-mono">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Engine: Sibyl Local Substrate
            </div>
          </div>

          {/* Product Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-white font-mono">Product</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/app" className="hover:text-white transition-colors flex items-center gap-1">
                  Live Console
                  <ArrowUpRight className="w-3 h-3 text-text-muted" />
                </Link>
              </li>
              <li>
                <Link href="/#architecture" className="hover:text-white transition-colors">
                  3-Tier Memory Architecture
                </Link>
              </li>
              <li>
                <Link href="/#features" className="hover:text-white transition-colors">
                  Cross-Domain Synthesis
                </Link>
              </li>
              <li>
                <Link href="/#delete-test" className="hover:text-white transition-colors">
                  The Delete Test Guarantee
                </Link>
              </li>
            </ul>
          </div>

          {/* Documentation Links */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-white font-mono">Documentation</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/docs#quickstart" className="hover:text-white transition-colors">
                  Quickstart Guide
                </Link>
              </li>
              <li>
                <Link href="/docs#record-api" className="hover:text-white transition-colors">
                  Core API (`record` & `brief`)
                </Link>
              </li>
              <li>
                <Link href="/docs#antigravity" className="hover:text-white transition-colors">
                  Antigravity Agent Bindings
                </Link>
              </li>
              <li>
                <Link href="/docs#rest-brief" className="hover:text-white transition-colors">
                  FastAPI REST Endpoints
                </Link>
              </li>
            </ul>
          </div>

          {/* Governance & Trust */}
          <div className="space-y-3">
            <h4 className="text-xs font-semibold uppercase tracking-wider text-white font-mono">Governance</h4>
            <ul className="space-y-2 text-xs">
              <li>
                <Link href="/privacy" className="hover:text-white transition-colors flex items-center gap-1">
                  <ShieldCheck className="w-3 h-3 text-indigo-400" />
                  Privacy & Data Sovereignty
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-white transition-colors">
                  Terms of Service & License
                </Link>
              </li>
              <li>
                <span className="text-[11px] text-text-muted block pt-2 font-mono">
                  MIT License · Local-first runtime
                </span>
              </li>
            </ul>
          </div>
        </div>

        {/* Baseline Divider */}
        <div className="pt-10 mt-12 border-t border-border-subtle flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-text-muted">
          <p>© {new Date().getFullYear()} Lumen Systems. All rights reserved.</p>
          <div className="flex items-center gap-6 font-mono text-[11px]">
            <span>STATUS: OPERATIONAL</span>
            <span>PORT: 8000</span>
            <span>LATENCY: &lt;2ms</span>
          </div>
        </div>
      </div>
    </footer>
  );
};
