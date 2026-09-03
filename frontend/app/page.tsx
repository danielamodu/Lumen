"use client";

import React, { useState } from "react";
import Link from "next/link";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import {
  Terminal,
  ArrowRight,
  GitFork,
  Code2,
  CheckCircle2,
  AlertTriangle,
  Flame,
  Snowflake,
  SunMedium,
  Copy,
  Check,
} from "lucide-react";

export default function MarketingPage() {
  const [activeTab, setActiveTab] = useState<"brief" | "record" | "agent">("brief");
  const [copiedCode, setCopiedCode] = useState(false);
  const [simulatedDomain, setSimulatedDomain] = useState<"pitch" | "post" | "ask">("pitch");

  const codeSnippets = {
    brief: `# 1. Before executing, agent requests an empirical brief
from lumen.core import brief

session_brief = brief(
    user_id="alex",
    domain="pitch",
    context="pitching an AI infrastructure fund on agent memory"
)

# Returns hot pre-computed heuristic:
# session_brief["warning"] -> "High loss rate (50%) when you 'opened with features'."
# session_brief["pattern"] -> "High win rate (50%) when you 'opened with the pain point'."
# session_brief["cross_domain"] -> "Your Ask domain shows 70% win rate leading with context."`,
    record: `# 2. After interaction completes, record observed signal
from lumen.core import record

# Signal: -1 (loss), 0 (neutral), 1 (win)
record(
    user_id="alex",
    domain="pitch",
    action="opened with the problem — agents forget everything",
    outcome="got a meeting booked same day",
    signal=1
)

# Automatically writes to COLD SQLite journal & re-indexes WARM pattern tier`,
    agent: `# 3. Plug into any autonomous agent in 3 lines
from google import genai
from lumen.core import record, brief

def run_pitch_turn(user_id: str, context: str):
    # Step A: Retrieve learned brief
    memory_brief = brief(user_id, "pitch", context)
    
    # Step B: Inject brief into system prompt
    prompt = f"Lumen Memory Brief:\\n{memory_brief}\\n\\nPrepare pitch for: {context}"
    response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
    
    # Step C: Return draft and record outcome upon completion
    return response.text`,
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedCode(true);
    setTimeout(() => setCopiedCode(false), 2000);
  };

  return (
    <div className="min-h-screen bg-canvas text-text-primary selection:bg-brand-500 selection:text-white">
      <Navbar />

      {/* Hero Section */}
      <section className="relative pt-20 pb-28 overflow-hidden border-b border-border-subtle">
        {/* Subtle ambient lighting */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[350px] bg-brand-500/10 blur-[140px] pointer-events-none rounded-full" />

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="max-w-3xl mx-auto text-center space-y-6">
            <div className="inline-flex items-center gap-2 bg-surface-2 border border-border-muted px-3.5 py-1.5 rounded-full text-xs font-mono text-indigo-300 shadow-sm">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span>LUMEN OUTCOME MEMORY SUBSTRATE v1.0</span>
            </div>

            <h1 className="text-4xl sm:text-6xl font-extrabold tracking-tight text-white leading-[1.12]">
              AI Agents Forget Everything. <br />
              <span className="font-display italic font-normal text-indigo-300 text-5xl sm:text-7xl">
                Lumen Gives Them Memory.
              </span>
            </h1>

            <p className="text-base sm:text-lg text-text-secondary leading-relaxed max-w-2xl mx-auto">
              A stateless agent that records wins and losses into Lumen gets smarter on every single turn. No fine-tuning, no bloated prompts, no prompt engineering. The memory does the learning.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4">
              <Link
                href="/app"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-sm px-6 py-3.5 rounded-xl transition-all shadow-glow hover:brightness-110 active:scale-[0.98]"
              >
                <Terminal className="w-4 h-4" />
                <span>Launch Live Console</span>
                <ArrowRight className="w-4 h-4" />
              </Link>
              <Link
                href="/docs"
                className="w-full sm:w-auto inline-flex items-center justify-center gap-2 bg-surface-2 hover:bg-surface-3 border border-border-muted text-text-secondary hover:text-white font-semibold text-sm px-6 py-3.5 rounded-xl transition-colors"
              >
                <Code2 className="w-4 h-4" />
                <span>Read Architecture Spec</span>
              </Link>
            </div>
          </div>

          {/* Live Interactive Memory Substrate Simulator */}
          <div className="mt-16 max-w-5xl mx-auto bg-surface-1 border border-border-subtle rounded-2xl shadow-elevated overflow-hidden">
            {/* Terminal Topbar */}
            <div className="flex items-center justify-between px-5 py-3.5 bg-surface-2 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full bg-rose-500/80" />
                <span className="w-3 h-3 rounded-full bg-amber-500/80" />
                <span className="w-3 h-3 rounded-full bg-emerald-500/80" />
                <span className="ml-2 text-xs font-mono text-text-muted">
                  lumen-memory-engine :: substrate_inspector
                </span>
              </div>
              <div className="flex items-center bg-surface-3 p-1 rounded-lg gap-1 border border-border-subtle">
                {(["pitch", "post", "ask"] as const).map((domain) => (
                  <button
                    key={domain}
                    onClick={() => setSimulatedDomain(domain)}
                    className={`px-3 py-1 rounded text-xs font-mono uppercase transition-all ${
                      simulatedDomain === domain
                        ? "bg-brand-500 text-white font-bold"
                        : "text-text-muted hover:text-white"
                    }`}
                  >
                    {domain}
                  </button>
                ))}
              </div>
            </div>

            {/* Terminal Body */}
            <div className="p-6 grid grid-cols-1 lg:grid-cols-3 gap-6 font-mono text-xs">
              {/* Cold Journal Column */}
              <div className="bg-canvas p-4 rounded-xl border border-border-subtle space-y-3">
                <div className="flex items-center justify-between text-text-muted pb-2 border-b border-border-subtle">
                  <span className="flex items-center gap-1.5 text-indigo-400 font-bold">
                    <Snowflake className="w-3.5 h-3.5" />
                    COLD JOURNAL
                  </span>
                  <span className="text-[10px] bg-surface-2 px-1.5 py-0.5 rounded">SQLite</span>
                </div>
                <div className="space-y-2 text-[11px] text-text-secondary leading-relaxed">
                  <div className="p-2.5 rounded bg-surface-1 border border-border-subtle">
                    <span className="text-emerald-400 font-bold">+1 WIN</span>: opened with pain point → meeting booked
                  </div>
                  <div className="p-2.5 rounded bg-surface-1 border border-border-subtle">
                    <span className="text-rose-400 font-bold">-1 LOSS</span>: opened with features → ghosted
                  </div>
                  <div className="p-2.5 rounded bg-surface-1 border border-border-subtle">
                    <span className="text-text-muted font-bold">0 NEUT</span>: generic deck share → deferred
                  </div>
                </div>
              </div>

              {/* Warm Pattern Column */}
              <div className="bg-canvas p-4 rounded-xl border border-border-subtle space-y-3">
                <div className="flex items-center justify-between text-text-muted pb-2 border-b border-border-subtle">
                  <span className="flex items-center gap-1.5 text-amber-400 font-bold">
                    <SunMedium className="w-3.5 h-3.5" />
                    WARM PATTERNS
                  </span>
                  <span className="text-[10px] bg-surface-2 px-1.5 py-0.5 rounded">Entities</span>
                </div>
                <div className="space-y-2 text-[11px]">
                  <div className="flex justify-between p-2.5 rounded bg-surface-1 border border-border-subtle">
                    <span className="text-text-muted">Total Outcomes:</span>
                    <span className="text-white font-bold">
                      {simulatedDomain === "pitch" ? "12" : simulatedDomain === "post" ? "11" : "10"}
                    </span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-surface-1 border border-border-subtle">
                    <span className="text-text-muted">Win Rate:</span>
                    <span className="text-emerald-400 font-bold">
                      {simulatedDomain === "pitch" ? "50%" : simulatedDomain === "post" ? "64%" : "70%"}
                    </span>
                  </div>
                  <div className="flex justify-between p-2.5 rounded bg-surface-1 border border-border-subtle">
                    <span className="text-text-muted">Confidence:</span>
                    <span className="text-indigo-300">Stable</span>
                  </div>
                </div>
              </div>

              {/* Hot Brief Column */}
              <div className="bg-canvas p-4 rounded-xl border border-border-subtle space-y-3">
                <div className="flex items-center justify-between text-text-muted pb-2 border-b border-border-subtle">
                  <span className="flex items-center gap-1.5 text-rose-400 font-bold">
                    <Flame className="w-3.5 h-3.5" />
                    HOT BRIEF
                  </span>
                  <span className="text-[10px] bg-surface-2 px-1.5 py-0.5 rounded">&lt;1ms</span>
                </div>
                <div className="p-3 rounded bg-surface-1 border border-border-subtle space-y-2 text-[11px] leading-relaxed">
                  <p className="text-rose-300">
                    <span className="text-rose-400 font-bold">WARN:</span> High loss rate with feature dump.
                  </p>
                  <p className="text-emerald-300">
                    <span className="text-emerald-400 font-bold">PATN:</span> Lead with customer pain point.
                  </p>
                  <p className="text-amber-300">
                    <span className="text-amber-400 font-bold">X-DOM:</span> Ask domain suggests leading with context.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Architecture & 3-Tier Memory Section */}
      <section id="architecture" className="py-24 border-b border-border-subtle bg-surface-1/40">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-4 mb-16">
            <span className="text-xs font-mono uppercase tracking-widest text-indigo-400 font-semibold">
              Memory Mechanics
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              The 3-Tier Outcome Substrate
            </h2>
            <p className="text-sm sm:text-base text-text-secondary leading-relaxed">
              Lumen separates raw empirical event storage from active reasoning so agents get instantaneous execution with zero prompt latency.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {/* Cold Tier */}
            <div className="bg-surface-1 rounded-2xl border border-border-subtle p-7 shadow-card relative group hover:border-border-muted transition-all">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400 mb-5">
                <Snowflake className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-indigo-400 font-bold">Tier 1 · Immutable</span>
              <h3 className="text-lg font-bold text-white mt-1 mb-2">COLD Journal</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Every action and observed outcome is recorded as an immutable, timestamped event in local SQLite. Forms the verifiable ground truth.
              </p>
              <div className="bg-canvas p-3 rounded-lg border border-border-subtle text-[11px] font-mono text-text-muted">
                LUMEN|alex|pitch|1|pain point|SEP|meeting booked
              </div>
            </div>

            {/* Warm Tier */}
            <div className="bg-surface-1 rounded-2xl border border-border-subtle p-7 shadow-card relative group hover:border-border-muted transition-all">
              <div className="w-10 h-10 rounded-xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 mb-5">
                <SunMedium className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-amber-400 font-bold">Tier 2 · Synthesized</span>
              <h3 className="text-lg font-bold text-white mt-1 mb-2">WARM Pattern Tier</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                On every write, Lumen recalculates user+domain statistics, isolating positive patterns, warning heuristics, and win-rate trajectories.
              </p>
              <div className="bg-canvas p-3 rounded-lg border border-border-subtle text-[11px] font-mono text-text-muted">
                win_rate: 0.50 | loss_rate: 0.50 | confidence: stable
              </div>
            </div>

            {/* Hot Tier */}
            <div className="bg-surface-1 rounded-2xl border border-border-subtle p-7 shadow-card relative group hover:border-border-muted transition-all">
              <div className="w-10 h-10 rounded-xl bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 mb-5">
                <Flame className="w-5 h-5" />
              </div>
              <span className="text-[11px] font-mono uppercase tracking-wider text-rose-400 font-bold">Tier 3 · Low Latency</span>
              <h3 className="text-lg font-bold text-white mt-1 mb-2">HOT Session State</h3>
              <p className="text-xs text-text-secondary leading-relaxed mb-4">
                Pre-formatted, token-optimized briefs cached for immediate injection into agent prompts with sub-millisecond overhead.
              </p>
              <div className="bg-canvas p-3 rounded-lg border border-border-subtle text-[11px] font-mono text-text-muted">
                brief:alex:pitch → warning + pattern + x_domain
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features & Cross-Domain Learning */}
      <section id="features" className="py-24 border-b border-border-subtle">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <div className="space-y-6">
              <span className="text-xs font-mono uppercase tracking-widest text-indigo-400 font-semibold">
                Autonomous Evolution
              </span>
              <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white leading-tight">
                Cross-Domain Synthesis: Learning Beyond a Single Task
              </h2>
              <p className="text-sm sm:text-base text-text-secondary leading-relaxed">
                When an agent learns in one domain, its insights don&apos;t remain trapped in a silo. Lumen traverses all domains for a user and cross-pollinates successful behavioral strategies.
              </p>

              <div className="space-y-4 pt-2">
                <div className="flex items-start gap-3.5 p-4 rounded-xl bg-surface-1 border border-border-subtle">
                  <div className="w-7 h-7 rounded-lg bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center text-emerald-400 shrink-0 mt-0.5">
                    <CheckCircle2 className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">Empirical Signal Weighting</h4>
                    <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">
                      Signals are strictly classified (-1 loss, 0 neutral, +1 win) without noisy subjective LLM hallucination.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 p-4 rounded-xl bg-surface-1 border border-border-subtle">
                  <div className="w-7 h-7 rounded-lg bg-amber-500/10 border border-amber-500/20 flex items-center justify-center text-amber-400 shrink-0 mt-0.5">
                    <GitFork className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">Cross-Domain Inference</h4>
                    <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">
                      If the Ask agent discovers that leading with context yields 70% win rate, the Pitch agent automatically receives this advice.
                    </p>
                  </div>
                </div>

                <div className="flex items-start gap-3.5 p-4 rounded-xl bg-surface-1 border border-border-subtle">
                  <div className="w-7 h-7 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 shrink-0 mt-0.5">
                    <AlertTriangle className="w-4 h-4" />
                  </div>
                  <div>
                    <h4 className="text-sm font-semibold text-white">Active Negative Constraint Heuristics</h4>
                    <p className="text-xs text-text-secondary mt-0.5 leading-relaxed">
                      Lumen issues specific warning directives when loss rates exceed thresholds, preventing agents from repeating historical failures.
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Interactive Visual Card */}
            <div className="bg-surface-1 border border-border-subtle rounded-2xl p-6 sm:p-8 shadow-card space-y-6">
              <div className="flex items-center justify-between pb-4 border-b border-border-subtle">
                <span className="text-xs font-mono uppercase text-white font-bold">CROSS_DOMAIN_SYNTHESIS_PIPELINE</span>
                <span className="text-[11px] font-mono text-emerald-400">ACTIVE</span>
              </div>

              <div className="space-y-4">
                <div className="p-4 rounded-xl bg-surface-2 border border-border-subtle space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-indigo-300 font-bold">SOURCE DOMAIN: ASK</span>
                    <span className="text-emerald-400 font-bold">70% WIN RATE</span>
                  </div>
                  <p className="text-xs text-text-secondary font-mono">
                    Learned: &quot;gave full context before asking&quot; wins consistently across 10 observations.
                  </p>
                </div>

                <div className="flex justify-center text-indigo-400">
                  <ArrowRight className="w-5 h-5 rotate-90" />
                </div>

                <div className="p-4 rounded-xl bg-surface-2 border border-border-subtle space-y-2">
                  <div className="flex items-center justify-between text-xs font-mono">
                    <span className="text-amber-300 font-bold">TARGET DOMAIN: PITCH</span>
                    <span className="text-indigo-300 font-bold">INJECTED BRIEF</span>
                  </div>
                  <p className="text-xs text-amber-200/90 font-mono">
                    &quot;Your Ask domain shows 70% win rate with &apos;gave full context before asking&apos;. Consider similar framing for pitch.&quot;
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Developer Experience / SDK Tabs */}
      <section className="py-24 border-b border-border-subtle bg-surface-1/30">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-4 mb-12">
            <span className="text-xs font-mono uppercase tracking-widest text-indigo-400 font-semibold">
              Developer Experience
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Drop-In Integration in 3 Lines of Python
            </h2>
            <p className="text-sm sm:text-base text-text-secondary leading-relaxed">
              Works seamlessly with Antigravity, LangChain, CrewAI, AutoGen, or custom raw API calls.
            </p>
          </div>

          <div className="max-w-4xl mx-auto bg-surface-1 border border-border-subtle rounded-2xl shadow-card overflow-hidden">
            {/* Tab Headers */}
            <div className="flex items-center justify-between px-6 py-3 bg-surface-2 border-b border-border-subtle">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => setActiveTab("brief")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                    activeTab === "brief"
                      ? "bg-brand-500 text-white font-bold shadow-sm"
                      : "text-text-muted hover:text-white"
                  }`}
                >
                  1. brief()
                </button>
                <button
                  onClick={() => setActiveTab("record")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                    activeTab === "record"
                      ? "bg-brand-500 text-white font-bold shadow-sm"
                      : "text-text-muted hover:text-white"
                  }`}
                >
                  2. record()
                </button>
                <button
                  onClick={() => setActiveTab("agent")}
                  className={`px-3 py-1.5 rounded-lg text-xs font-mono font-medium transition-all ${
                    activeTab === "agent"
                      ? "bg-brand-500 text-white font-bold shadow-sm"
                      : "text-text-muted hover:text-white"
                  }`}
                >
                  3. Agent Loop
                </button>
              </div>

              <button
                onClick={() => copyToClipboard(codeSnippets[activeTab])}
                className="flex items-center gap-1.5 text-xs text-text-muted hover:text-white font-mono bg-surface-3 px-2.5 py-1 rounded border border-border-subtle transition-colors"
              >
                {copiedCode ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5" />}
                <span>{copiedCode ? "Copied" : "Copy Code"}</span>
              </button>
            </div>

            {/* Code Block */}
            <pre className="p-6 text-xs sm:text-sm font-mono leading-relaxed text-indigo-100 bg-canvas overflow-x-auto">
              <code>{codeSnippets[activeTab]}</code>
            </pre>
          </div>
        </div>
      </section>

      {/* Delete Test / Load-Bearing Proof */}
      <section id="delete-test" className="py-24 border-b border-border-subtle">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl mx-auto text-center space-y-4 mb-16">
            <span className="text-xs font-mono uppercase tracking-widest text-rose-400 font-semibold">
              The Delete Test
            </span>
            <h2 className="text-3xl sm:text-4xl font-bold tracking-tight text-white">
              Why Memory is Load-Bearing
            </h2>
            <p className="text-sm sm:text-base text-text-secondary leading-relaxed">
              If an architecture can delete its memory without losing competence, that memory was cosmetic. When you delete Sibyl memory in Lumen, the agent goes completely blind.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
            <div className="bg-surface-1 border border-border-subtle rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-emerald-400 text-sm font-bold font-mono">
                <CheckCircle2 className="w-4 h-4" />
                WITH SIBYL MEMORY
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">
                Agent knows exactly which strategies failed historically, what pain points converted, and what context was needed from adjacent domains.
              </p>
              <div className="p-3 rounded-lg bg-surface-2 border border-border-subtle font-mono text-[11px] text-emerald-300">
                raw_outcomes: 14 · confidence: stable · warning: active
              </div>
            </div>

            <div className="bg-surface-1 border border-rose-900/40 rounded-2xl p-6 space-y-4">
              <div className="flex items-center gap-2 text-rose-400 text-sm font-bold font-mono">
                <AlertTriangle className="w-4 h-4" />
                AFTER MEMORY WIPE
              </div>
              <p className="text-xs text-text-secondary leading-relaxed">
                All learned heuristics evaporate. The agent falls back to baseline guessing and is destined to repeat the exact same loss pattern.
              </p>
              <div className="p-3 rounded-lg bg-rose-950/20 border border-rose-900/30 font-mono text-[11px] text-rose-300">
                raw_outcomes: 0 · confidence: None · warning: None
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Pre-Footer CTA */}
      <section className="py-20 relative">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h2 className="text-3xl sm:text-4xl font-extrabold text-white tracking-tight">
            Experience Autonomous Outcome Learning Live
          </h2>
          <p className="text-sm sm:text-base text-text-secondary max-w-xl mx-auto">
            Test the interactive 5-step loop sequence or record real actions directly into your local Sibyl substrate.
          </p>
          <div className="pt-2">
            <Link
              href="/app"
              className="inline-flex items-center gap-2 bg-brand-500 hover:bg-brand-600 text-white font-semibold text-sm px-8 py-3.5 rounded-xl transition-all shadow-glow hover:brightness-110 active:scale-[0.98]"
            >
              <Terminal className="w-4 h-4" />
              <span>Open Lumen Live Console</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </section>

      <Footer />
    </div>
  );
}
