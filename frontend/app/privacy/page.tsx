import React from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { ShieldCheck, HardDrive, Trash2, EyeOff } from "lucide-react";

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-canvas text-text-primary selection:bg-brand-500 selection:text-white flex flex-col justify-between">
      <div>
        <Navbar />

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-12">
          {/* Header */}
          <div className="space-y-4 border-b border-border-subtle pb-8">
            <div className="inline-flex items-center gap-2 text-xs font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-3 py-1 rounded-full">
              <ShieldCheck className="w-3.5 h-3.5" />
              PRIVACY & DATA SOVEREIGNTY SPECIFICATION
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Privacy Policy
            </h1>
            <p className="text-xs sm:text-sm text-text-muted font-mono">
              Last updated: September 2026 · Protocol Version 1.0
            </p>
          </div>

          {/* Core Principles Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-5 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
              <HardDrive className="w-5 h-5 text-indigo-400" />
              <h3 className="text-sm font-bold text-white">Local-First Storage</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                All outcomes, entities, and journal events reside exclusively in your local filesystem (`~/.sibyl-memory`).
              </p>
            </div>

            <div className="p-5 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
              <EyeOff className="w-5 h-5 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">Zero Telemetry</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Lumen does not phone home, log user prompts to remote servers, or share empirical agent data with third parties.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
              <Trash2 className="w-5 h-5 text-rose-400" />
              <h3 className="text-sm font-bold text-white">Total Erasure Guarantee</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Deleting the SQLite database immediately and irrecoverably purges 100% of recorded outcomes and learned patterns.
              </p>
            </div>
          </div>

          {/* Policy Body */}
          <div className="space-y-8 text-sm text-text-secondary leading-relaxed">
            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">1. Data Architecture and Isolation</h2>
              <p>
                Lumen functions as an embedded outcome memory substrate for AI systems. When an application calls `lumen.core.record()` or `lumen.core.brief()`, data is written directly to a local SQLite database utilizing the Sibyl memory engine. No network requests are dispatched to external telemetry or training endpoints during standard operation.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">2. Scope of Collected Empirical Data</h2>
              <p>Lumen only stores the structured parameters provided explicitly by the developer:</p>
              <ul className="list-disc list-inside space-y-1 text-xs font-mono text-indigo-200">
                <li>`user_id` — A local workspace or user partition key.</li>
                <li>`domain` — The operational task category (e.g. pitch, post, ask).</li>
                <li>`action` — The textual description of what the agent tried.</li>
                <li>`outcome` — The textual description of what happened.</li>
                <li>`signal` — An integer value (-1 for loss, 0 for neutral, 1 for win).</li>
              </ul>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">3. Cryptographic and Access Security</h2>
              <p>
                The underlying Sibyl storage layer applies strict filesystem permissions (POSIX `0600` for database files and `0700` for memory directories) to prevent cross-process data leakage on shared systems.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">4. Total Wipe & User Control</h2>
              <p>
                Developers and end-users retain absolute sovereignty over their data. Calling `POST /wipe` or deleting `~/.sibyl-memory/lumen_demo.db` immediately eliminates all cold journal logs, warm pattern entities, and hot session caches.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">5. Contact and Open Governance</h2>
              <p>
                Lumen is open-source software governed by the MIT License. For inquiries regarding memory architecture or security disclosures, refer to the project repository.
              </p>
            </section>
          </div>
        </main>
      </div>

      <Footer />
    </div>
  );
}
