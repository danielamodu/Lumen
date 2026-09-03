"use client";

import React, { useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import {
  Cpu,
  Copy,
  Check,
} from "lucide-react";

export default function DocsPage() {
  const [copiedSection, setCopiedSection] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedSection(id);
    setTimeout(() => setCopiedSection(null), 2000);
  };

  return (
    <div className="min-h-screen bg-canvas text-text-primary selection:bg-brand-500 selection:text-white">
      <Navbar />

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-12">
          {/* Left Sticky Sidebar */}
          <aside className="hidden lg:block lg:col-span-1">
            <div className="sticky top-24 space-y-6 text-xs font-mono">
              <div className="pb-3 border-b border-border-subtle">
                <span className="text-white font-bold uppercase tracking-wider block mb-1">
                  Lumen Documentation
                </span>
                <span className="text-[11px] text-text-muted">Version 1.0.0 (2026)</span>
              </div>

              <nav className="space-y-4">
                <div>
                  <h4 className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider mb-2">
                    Getting Started
                  </h4>
                  <ul className="space-y-1.5 text-text-secondary">
                    <li>
                      <a href="#overview" className="hover:text-white transition-colors block py-0.5">
                        Overview & Mental Model
                      </a>
                    </li>
                    <li>
                      <a href="#quickstart" className="hover:text-white transition-colors block py-0.5">
                        Quickstart Installation
                      </a>
                    </li>
                    <li>
                      <a href="#architecture-tiers" className="hover:text-white transition-colors block py-0.5">
                        3-Tier Memory Architecture
                      </a>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider mb-2">
                    Python Core SDK
                  </h4>
                  <ul className="space-y-1.5 text-text-secondary">
                    <li>
                      <a href="#record-api" className="hover:text-white transition-colors block py-0.5">
                        `lumen.core.record()`
                      </a>
                    </li>
                    <li>
                      <a href="#brief-api" className="hover:text-white transition-colors block py-0.5">
                        `lumen.core.brief()`
                      </a>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider mb-2">
                    Agent Frameworks
                  </h4>
                  <ul className="space-y-1.5 text-text-secondary">
                    <li>
                      <a href="#antigravity" className="hover:text-white transition-colors block py-0.5">
                        Antigravity Native Agents
                      </a>
                    </li>
                  </ul>
                </div>

                <div>
                  <h4 className="text-[11px] font-bold text-indigo-400 uppercase tracking-wider mb-2">
                    FastAPI REST Endpoints
                  </h4>
                  <ul className="space-y-1.5 text-text-secondary">
                    <li>
                      <a href="#rest-brief" className="hover:text-white transition-colors block py-0.5">
                        POST /brief
                      </a>
                    </li>
                    <li>
                      <a href="#rest-record" className="hover:text-white transition-colors block py-0.5">
                        POST /record
                      </a>
                    </li>
                    <li>
                      <a href="#rest-demo" className="hover:text-white transition-colors block py-0.5">
                        POST /demo/step
                      </a>
                    </li>
                    <li>
                      <a href="#rest-wipe" className="hover:text-white transition-colors block py-0.5">
                        POST /wipe
                      </a>
                    </li>
                  </ul>
                </div>
              </nav>
            </div>
          </aside>

          {/* Main Content Area */}
          <main className="lg:col-span-3 space-y-16">
            {/* Overview */}
            <section id="overview" className="space-y-4">
              <div className="inline-flex items-center gap-2 text-xs font-mono text-indigo-400 bg-surface-2 border border-border-subtle px-3 py-1 rounded-full">
                <Cpu className="w-3.5 h-3.5" />
                FOUNDATIONAL SPECIFICATION
              </div>
              <h1 className="text-3xl font-extrabold text-white tracking-tight">
                Lumen Outcome Memory Layer
              </h1>
              <p className="text-sm text-text-secondary leading-relaxed">
                Lumen is an outcome memory layer for AI agents. Any agent can write outcomes to it and read learned patterns from it. The core insight: agents that plug into Lumen get smarter over time without being designed to learn. The memory does the learning.
              </p>
              <div className="p-4 rounded-xl bg-surface-1 border border-border-subtle text-xs text-text-secondary leading-relaxed space-y-2">
                <p className="font-semibold text-white">Why prompt engineering fails at scale:</p>
                <p>
                  Stateless LLMs reset between execution loops. Prompt stuffing causes context bloat and hallucination. Lumen introduces a deterministic, empirical feedback loop backed by Sibyl SQLite memory.
                </p>
              </div>
            </section>

            {/* Quickstart */}
            <section id="quickstart" className="space-y-4">
              <h2 className="text-xl font-bold text-white tracking-tight border-b border-border-subtle pb-2">
                Quickstart & Installation
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Install Lumen core and dependencies using pip:
              </p>

              <div className="bg-surface-1 border border-border-subtle rounded-xl overflow-hidden font-mono text-xs">
                <div className="flex items-center justify-between px-4 py-2 bg-surface-2 border-b border-border-subtle text-text-muted">
                  <span>Terminal</span>
                  <button
                    onClick={() => handleCopy("pip", "pip install sibyl-memory-client==0.8.0 pytest fastapi uvicorn")}
                    className="hover:text-white flex items-center gap-1"
                  >
                    {copiedSection === "pip" ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedSection === "pip" ? "Copied" : "Copy"}</span>
                  </button>
                </div>
                <pre className="p-4 text-indigo-200">
                  <code>pip install sibyl-memory-client==0.8.0 pytest fastapi uvicorn</code>
                </pre>
              </div>
            </section>

            {/* 3-Tier Architecture */}
            <section id="architecture-tiers" className="space-y-4">
              <h2 className="text-xl font-bold text-white tracking-tight border-b border-border-subtle pb-2">
                3-Tier Memory Architecture
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Lumen organizes memory into three distinct operational tiers to balance immutability, pattern synthesis, and execution speed:
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="bg-surface-1 border border-border-subtle p-4 rounded-xl space-y-2">
                  <span className="text-[10px] font-mono font-bold text-indigo-400 uppercase">Tier 1 · COLD</span>
                  <h4 className="text-sm font-bold text-white">Event Journal</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    Append-only raw interaction logs stored in SQLite. Holds full historical ground truth.
                  </p>
                </div>

                <div className="bg-surface-1 border border-border-subtle p-4 rounded-xl space-y-2">
                  <span className="text-[10px] font-mono font-bold text-amber-400 uppercase">Tier 2 · WARM</span>
                  <h4 className="text-sm font-bold text-white">Pattern Entities</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    Recalculated on write. Computes win rates, recent loss clusters, and cross-domain links.
                  </p>
                </div>

                <div className="bg-surface-1 border border-border-subtle p-4 rounded-xl space-y-2">
                  <span className="text-[10px] font-mono font-bold text-rose-400 uppercase">Tier 3 · HOT</span>
                  <h4 className="text-sm font-bold text-white">Session State</h4>
                  <p className="text-xs text-text-secondary leading-relaxed">
                    In-memory brief cache. Ready for instant zero-latency injection into agent context.
                  </p>
                </div>
              </div>
            </section>

            {/* record API */}
            <section id="record-api" className="space-y-4">
              <h2 className="text-xl font-bold text-white tracking-tight border-b border-border-subtle pb-2 font-mono">
                lumen.core.record()
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Writes one outcome to Sibyl COLD memory and immediately triggers pattern recalculation for that user and domain.
              </p>

              <div className="bg-surface-1 border border-border-subtle rounded-xl overflow-hidden font-mono text-xs">
                <div className="flex items-center justify-between px-4 py-2 bg-surface-2 border-b border-border-subtle text-text-muted">
                  <span>python · record()</span>
                  <button
                    onClick={() =>
                      handleCopy(
                        "rec",
                        `record(user_id="alex", domain="pitch", action="opened with problem", outcome="meeting booked", signal=1)`
                      )
                    }
                    className="hover:text-white flex items-center gap-1"
                  >
                    {copiedSection === "rec" ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedSection === "rec" ? "Copied" : "Copy"}</span>
                  </button>
                </div>
                <pre className="p-4 text-indigo-200">
                  <code>{`from lumen.core import record

record(
    user_id="alex",
    domain="pitch",
    action="opened with the problem — agents forget everything",
    outcome="got a meeting booked same day",
    signal=1  # -1 (loss), 0 (neutral), 1 (win)
)`}</code>
                </pre>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs font-mono border border-border-subtle rounded-lg">
                  <thead className="bg-surface-2 text-white border-b border-border-subtle">
                    <tr>
                      <th className="p-2.5">Parameter</th>
                      <th className="p-2.5">Type</th>
                      <th className="p-2.5">Description</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border-subtle text-text-secondary">
                    <tr>
                      <td className="p-2.5 text-indigo-300">user_id</td>
                      <td className="p-2.5">str</td>
                      <td className="p-2.5">Unique identifier for the user / workspace</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 text-indigo-300">domain</td>
                      <td className="p-2.5">str</td>
                      <td className="p-2.5">Domain identifier: &quot;pitch&quot;, &quot;post&quot;, &quot;ask&quot;</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 text-indigo-300">action</td>
                      <td className="p-2.5">str</td>
                      <td className="p-2.5">What the agent or user attempted</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 text-indigo-300">outcome</td>
                      <td className="p-2.5">str</td>
                      <td className="p-2.5">What empirical result occurred</td>
                    </tr>
                    <tr>
                      <td className="p-2.5 text-indigo-300">signal</td>
                      <td className="p-2.5">int</td>
                      <td className="p-2.5">-1 (loss), 0 (neutral), or 1 (win)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            {/* brief API */}
            <section id="brief-api" className="space-y-4">
              <h2 className="text-xl font-bold text-white tracking-tight border-b border-border-subtle pb-2 font-mono">
                lumen.core.brief()
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Reads the synthesized WARM pattern entity and cached HOT state to generate an actionable pre-turn brief.
              </p>

              <div className="bg-surface-1 border border-border-subtle rounded-xl overflow-hidden font-mono text-xs">
                <div className="flex items-center justify-between px-4 py-2 bg-surface-2 border-b border-border-subtle text-text-muted">
                  <span>python · brief()</span>
                  <button
                    onClick={() =>
                      handleCopy(
                        "brf",
                        `session_brief = brief(user_id="alex", domain="pitch", context="about to pitch fund")`
                      )
                    }
                    className="hover:text-white flex items-center gap-1"
                  >
                    {copiedSection === "brf" ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                    <span>{copiedSection === "brf" ? "Copied" : "Copy"}</span>
                  </button>
                </div>
                <pre className="p-4 text-indigo-200">
                  <code>{`from lumen.core import brief

result = brief(
    user_id="alex",
    domain="pitch",
    context="about to pitch an enterprise crypto fund"
)

print(result)
# {
#   "warning": "High loss rate (50%) when you 'opened with features'...",
#   "pattern": "High win rate (50%) when you 'opened with the pain point'...",
#   "cross_domain": "Your Ask domain shows 70% win rate...",
#   "confidence": "12 outcomes recorded. Pattern is stable.",
#   "raw_outcomes": 12
# }`}</code>
                </pre>
              </div>
            </section>

            {/* Antigravity Integration */}
            <section id="antigravity" className="space-y-4">
              <h2 className="text-xl font-bold text-white tracking-tight border-b border-border-subtle pb-2">
                Antigravity Agent Framework Bindings
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Integrating Lumen with Google Antigravity preview models requires only injecting the brief into the initial turn context:
              </p>

              <div className="bg-surface-1 border border-border-subtle rounded-xl overflow-hidden font-mono text-xs">
                <pre className="p-4 text-indigo-200">
                  <code>{`from google import genai
from lumen.core import record, brief

client = genai.Client()

def interact_with_agent(user_id: str, domain: str, context: str):
    # 1. Pull empirical brief
    b = brief(user_id, domain, context)

    # 2. Synthesize prompt
    system_instruction = f"Lumen Memory Brief:\\n{b}"
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"Execute task: {context}",
        config=genai.types.GenerateContentConfig(system_instruction=system_instruction)
    )

    # 3. Output and later record result
    return response.text`}</code>
                </pre>
              </div>
            </section>

            {/* REST API */}
            <section id="rest-brief" className="space-y-4">
              <h2 className="text-xl font-bold text-white tracking-tight border-b border-border-subtle pb-2">
                FastAPI REST Service
              </h2>
              <p className="text-xs text-text-secondary leading-relaxed">
                Lumen includes an asynchronous FastAPI backend running on port 8000 for web and microservice integrations:
              </p>

              <div className="space-y-4 font-mono text-xs">
                <div className="p-4 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-500/20 text-emerald-300 font-bold px-2 py-0.5 rounded">POST</span>
                    <span className="text-white font-bold">/brief</span>
                  </div>
                  <p className="text-text-muted">Body: {`{ "user_id": "alex", "domain": "pitch", "context": "testing" }`}</p>
                </div>

                <div className="p-4 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="bg-emerald-500/20 text-emerald-300 font-bold px-2 py-0.5 rounded">POST</span>
                    <span className="text-white font-bold">/record</span>
                  </div>
                  <p className="text-text-muted">Body: {`{ "user_id": "alex", "domain": "pitch", "action": "...", "outcome": "...", "signal": 1 }`}</p>
                </div>

                <div className="p-4 rounded-xl bg-surface-1 border border-border-subtle space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="bg-indigo-500/20 text-indigo-300 font-bold px-2 py-0.5 rounded">POST</span>
                    <span className="text-white font-bold">/demo/step</span>
                  </div>
                  <p className="text-text-muted">Body: {`{ "step": 1 }`} (Runs automated loop demo step 1 through 5)</p>
                </div>

                <div className="p-4 rounded-xl bg-surface-1 border border-rose-900/30 space-y-2">
                  <div className="flex items-center gap-2">
                    <span className="bg-rose-500/20 text-rose-300 font-bold px-2 py-0.5 rounded">POST</span>
                    <span className="text-rose-300 font-bold">/wipe</span>
                  </div>
                  <p className="text-text-muted">Body: {`{}`} (Purges local SQLite memory DB)</p>
                </div>
              </div>
            </section>
          </main>
        </div>
      </div>

      <Footer />
    </div>
  );
}
