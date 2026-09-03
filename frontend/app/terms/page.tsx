import React from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Scale, CheckCircle2, AlertTriangle } from "lucide-react";

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-canvas text-text-primary selection:bg-brand-500 selection:text-white flex flex-col justify-between">
      <div>
        <Navbar />

        <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-12">
          {/* Header */}
          <div className="space-y-4 border-b border-border-subtle pb-8">
            <div className="inline-flex items-center gap-2 text-xs font-mono text-indigo-400 bg-surface-2 border border-border-subtle px-3 py-1 rounded-full">
              <Scale className="w-3.5 h-3.5" />
              LEGAL TERMS & OPEN SOFTWARE LICENSE
            </div>
            <h1 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
              Terms of Service
            </h1>
            <p className="text-xs sm:text-sm text-text-muted font-mono">
              Effective Date: September 2026 · Standard Developer Terms
            </p>
          </div>

          {/* Highlights */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-5 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
              <CheckCircle2 className="w-5 h-5 text-emerald-400" />
              <h3 className="text-sm font-bold text-white">MIT Permissive License</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                You are free to use, modify, distribute, and embed Lumen in commercial or open-source software applications without licensing royalties.
              </p>
            </div>

            <div className="p-5 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              <h3 className="text-sm font-bold text-white">Autonomous Agent Liability</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Lumen provides memory synthesis and pattern heuristics. Developers remain solely responsible for actions taken by their autonomous AI agents.
              </p>
            </div>
          </div>

          {/* Terms Content */}
          <div className="space-y-8 text-sm text-text-secondary leading-relaxed">
            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">1. Acceptance of Terms</h2>
              <p>
                By accessing, installing, running, or embedding the Lumen software (including the core Python package, FastAPI server, and Next.js console), you agree to be bound by these Terms of Service.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">2. Open Source Grant</h2>
              <p>
                Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files, to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">3. Disclaimers of Warranty</h2>
              <p>
                THE SOFTWARE IS PROVIDED &quot;AS IS&quot;, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">4. Autonomous Agent Operations</h2>
              <p>
                Lumen acts as a deterministic feedback substrate that reflects historical outcomes recorded by the host system. The software does not provide legal, financial, or guaranteed operational advice. Developers must enforce appropriate guardrails and human-in-the-loop controls for high-stakes agent operations.
              </p>
            </section>

            <section className="space-y-3">
              <h2 className="text-base font-bold text-white">5. Governing Jurisdiction</h2>
              <p>
                These terms are governed by standard open-source conventions. No rights or obligations beyond those set forth in the MIT license apply.
              </p>
            </section>
          </div>
        </main>
      </div>

      <Footer />
    </div>
  );
}
