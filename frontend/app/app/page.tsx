"use client";

import React, { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { apiFetch } from "@/lib/api";

interface BriefData {
  domain?: string;
  raw_outcomes?: number;
  count?: number;
  confidence?: string;
  confidence_score?: number;
  confidence_percent?: number;
  warning?: string | null;
  pattern?: string | null;
  cross_domain?: string | null;
}

interface EventEntry {
  user_id: string;
  domain: string;
  signal: number;
  action: string;
  outcome: string;
  timestamp?: string;
  created_at?: string;
  raw?: string;
}

interface PatternEntry {
  user_id: string;
  domain: string;
  win_rate: number;
  loss_rate: number;
  avg_signal: number;
  recent_wins: string[];
  recent_losses: string[];
  total_outcomes: number;
  last_calculated: string;
}

const TIMELINE_STEPS = [
  {
    name: "Cold write",
    desc: "Outcome appended to the journal.",
    action: "record() → COLD JOURNAL",
  },
  {
    name: "Pattern extraction",
    desc: "History becomes a living pattern.",
    action: "recalculate() → WARM PATTERN",
  },
  {
    name: "Brief formation",
    desc: "The agent receives a memory-aware brief.",
    action: "brief() → HOT CONTEXT",
  },
  {
    name: "Behavioral fork",
    desc: "The next action changes.",
    action: "agent.choose(pattern)",
  },
  {
    name: "Proof of learning",
    desc: "A new outcome closes the loop.",
    action: "record() → loop complete",
  },
];

export default function LiveConsolePage() {
  // Domain briefs
  const [pitchBrief, setPitchBrief] = useState<BriefData>({
    raw_outcomes: 0,
    confidence: "Insufficient data",
    warning: null,
    pattern: null,
    cross_domain: null,
  });
  const [postBrief, setPostBrief] = useState<BriefData>({
    raw_outcomes: 0,
    confidence: "Insufficient data",
    warning: null,
    pattern: null,
    cross_domain: null,
  });
  const [askBrief, setAskBrief] = useState<BriefData>({
    raw_outcomes: 0,
    confidence: "Insufficient data",
    warning: null,
    pattern: null,
    cross_domain: null,
  });

  // Active tab in Memory Inspector
  const [activeTab, setActiveTab] = useState<"cold" | "warm">("cold");

  // Cold journal events
  const [events, setEvents] = useState<EventEntry[]>([]);
  const [loadingEvents, setLoadingEvents] = useState(false);

  // Warm patterns
  const [patterns, setPatterns] = useState<PatternEntry[]>([]);
  const [loadingPatterns, setLoadingPatterns] = useState(false);

  // Outcome Recorder form state
  const [selectedDomain, setSelectedDomain] = useState<"pitch" | "post" | "ask">("pitch");
  const [recordContext, setRecordContext] = useState("");
  const [recordAction, setRecordAction] = useState("");
  const [recordOutcome, setRecordOutcome] = useState("");
  const [activeSignal, setActiveSignal] = useState<number>(0);
  const [showToast, setShowToast] = useState(false);
  const [recorderBrief, setRecorderBrief] = useState<BriefData | null>(null);
  const [isSubmittingOutcome, setIsSubmittingOutcome] = useState(false);
  const [isGettingBrief, setIsGettingBrief] = useState(false);

  // Watch Lumen learn demo step
  const [currentDemoStep, setCurrentDemoStep] = useState(0);
  const [isStepRunning, setIsStepRunning] = useState(false);

  // Seeding and wiping states
  const [isSeeding, setIsSeeding] = useState(false);

  // Helper to compute confidence percentage
  const getConfidencePercent = (brief: BriefData) => {
    const count = brief.raw_outcomes ?? brief.count ?? 0;
    if (brief.confidence_percent !== undefined) {
      return Math.max(0, Math.min(100, brief.confidence_percent));
    }
    if (brief.confidence_score !== undefined) {
      return Math.max(0, Math.min(100, Math.round(brief.confidence_score * 100)));
    }
    // Per requirement: (raw_outcomes / 30) * 100 capped at 100%
    return Math.max(0, Math.min(100, Math.round((count / 30) * 100)));
  };

  // Fetch brief for a domain
  const fetchDomainBrief = useCallback(async (domain: "pitch" | "post" | "ask", context = "") => {
    try {
      const data = await apiFetch<BriefData>("/brief", {
        user_id: "alex",
        domain,
        context,
      });
      if (domain === "pitch") setPitchBrief(data);
      else if (domain === "post") setPostBrief(data);
      else if (domain === "ask") setAskBrief(data);
      return data;
    } catch (err) {
      console.warn(`Failed to fetch brief for ${domain}:`, err);
      return null;
    }
  }, []);

  // Fetch events for Cold Journal
  const fetchEvents = useCallback(async () => {
    setLoadingEvents(true);
    try {
      const data = await apiFetch<{ events: EventEntry[]; count: number }>("/memory/events", {
        user_id: "alex",
      });
      setEvents(data.events || []);
    } catch (err) {
      console.warn("Failed to fetch events:", err);
    } finally {
      setLoadingEvents(false);
    }
  }, []);

  // Fetch patterns for Warm Tier
  const fetchPatterns = useCallback(async () => {
    setLoadingPatterns(true);
    try {
      const data = await apiFetch<{ patterns: PatternEntry[]; count: number }>("/memory/patterns", {
        user_id: "alex",
      });
      setPatterns(data.patterns || []);
    } catch (err) {
      console.warn("Failed to fetch patterns:", err);
    } finally {
      setLoadingPatterns(false);
    }
  }, []);

  // Refresh all components
  const refreshAll = useCallback(() => {
    fetchDomainBrief("pitch");
    fetchDomainBrief("post");
    fetchDomainBrief("ask");
    fetchEvents();
    fetchPatterns();
  }, [fetchDomainBrief, fetchEvents, fetchPatterns]);

  // Initial load and 10s auto-refresh
  useEffect(() => {
    refreshAll();
    const interval = setInterval(() => {
      fetchEvents();
    }, 10000);
    return () => clearInterval(interval);
  }, [refreshAll, fetchEvents]);

  // Calculate total outcomes across all domains
  const pitchCount = pitchBrief.raw_outcomes ?? pitchBrief.count ?? 0;
  const postCount = postBrief.raw_outcomes ?? postBrief.count ?? 0;
  const askCount = askBrief.raw_outcomes ?? askBrief.count ?? 0;
  const totalOutcomes = pitchCount + postCount + askCount;

  // Handler: Seed 33 outcomes
  const handleSeed = async () => {
    setIsSeeding(true);
    try {
      await apiFetch("/seed", {});
      refreshAll();
    } catch (err) {
      console.error("Seed error:", err);
      alert("Failed to seed memory. Check API connection.");
    } finally {
      setIsSeeding(false);
    }
  };

  // Handler: Get brief before acting for recorder
  const handleGetBriefForRecorder = async () => {
    setIsGettingBrief(true);
    try {
      const brief = await fetchDomainBrief(selectedDomain, recordContext);
      setRecorderBrief(brief);
    } finally {
      setIsGettingBrief(false);
    }
  };

  // Handler: Submit outcome
  const handleSubmitOutcome = async () => {
    if (!recordAction.trim() || !recordOutcome.trim()) {
      alert("Please enter both action taken and observed outcome.");
      return;
    }

    setIsSubmittingOutcome(true);
    try {
      await apiFetch("/record", {
        user_id: "alex",
        domain: selectedDomain,
        action: recordAction.trim(),
        outcome: recordOutcome.trim(),
        signal: activeSignal,
        context: recordContext.trim(),
      });

      setShowToast(true);
      setTimeout(() => setShowToast(false), 2000);

      setRecordAction("");
      setRecordOutcome("");
      setRecorderBrief(null);
      refreshAll();
    } catch (err) {
      console.error("Record outcome failed:", err);
      alert("Failed to record outcome. Check API status.");
    } finally {
      setIsSubmittingOutcome(false);
    }
  };

  // Handler: Run next demo step
  const handleRunNextStep = async () => {
    if (currentDemoStep >= 5 || isStepRunning) return;
    const nextStep = currentDemoStep + 1;
    setIsStepRunning(true);
    try {
      await apiFetch("/demo/step", { step: nextStep });
      setCurrentDemoStep(nextStep);
      refreshAll();
    } catch (err) {
      console.error("Demo step failed:", err);
    } finally {
      setIsStepRunning(false);
    }
  };

  // Handler: Reset demo
  const handleResetDemo = async () => {
    try {
      await apiFetch("/demo/step", { step: 5 });
    } catch (err) {
      console.warn("Reset error:", err);
    }
    setCurrentDemoStep(0);
    refreshAll();
  };

  // Handler: Confirm wipe
  const handleConfirmWipe = async () => {
    const ok = window.confirm(
      "Delete all Sibyl memory? This proves the load-bearing test. All patterns will be lost."
    );
    if (!ok) return;

    try {
      await apiFetch("/wipe", {});
      setPitchBrief({ raw_outcomes: 0, confidence: "0 outcomes recorded. No pattern yet." });
      setPostBrief({ raw_outcomes: 0, confidence: "0 outcomes recorded. No pattern yet." });
      setAskBrief({ raw_outcomes: 0, confidence: "0 outcomes recorded. No pattern yet." });
      setEvents([]);
      setPatterns([]);
      refreshAll();
    } catch (err) {
      console.error("Wipe failed:", err);
      alert("Wipe failed. Check server permissions.");
    }
  };

  const pitchPct = getConfidencePercent(pitchBrief);
  const postPct = getConfidencePercent(postBrief);
  const askPct = getConfidencePercent(askBrief);

  return (
    <div className="min-h-screen bg-[#0C0A09] text-[#E7E5E4] selection:bg-lime-400/20 selection:text-lime-300">
      <div className="noise-overlay" />
      <div className="min-h-screen grid-field">
        {/* Header */}
        <header className="fixed top-0 left-0 w-full live-header z-50 border-b border-white/10">
          <div className="px-4 sm:px-6 py-4 flex items-center justify-between max-w-[1600px] mx-auto">
            <Link href="/" id="nav-logo-link" className="flex items-center gap-3 group">
              <div className="w-11 h-11 rounded-2xl bg-gradient-to-br from-lime-300 to-lime-500 text-stone-950 flex items-center justify-center shadow-lg shadow-lime-400/10 group-hover:rotate-6 transition-transform">
                <iconify-icon icon="lucide:brain-circuit" class="text-2xl" />
              </div>
              <div>
                <div className="text-[10px] text-white/40 uppercase tracking-[.28em]">Lumen / 01</div>
                <div className="serif-display text-2xl italic leading-none group-hover:text-lime-300 transition-colors">
                  Live Console
                </div>
              </div>
            </Link>

            <div className="header-actions flex items-center gap-3 sm:gap-6">
              {/* Header status indicator */}
              <div
                id="status-indicator"
                className="flex items-center gap-2 px-3 py-2 rounded-full bg-white/[.04] border border-white/10"
              >
                <span
                  className={`status-dot w-2 h-2 rounded-full ${
                    totalOutcomes > 0 ? "bg-lime-400 animate-pulse" : "bg-red-500"
                  }`}
                />
                <span className="status-label text-[10px] uppercase tracking-widest text-white/60">
                  {totalOutcomes > 0 ? (
                    <>
                      MEMORY ACTIVE (
                      <span id="total-outcomes-count" className="text-lime-300">
                        {totalOutcomes}
                      </span>{" "}
                      OUTCOMES)
                    </>
                  ) : (
                    <span className="text-red-400">MEMORY EMPTY</span>
                  )}
                </span>
              </div>

              {/* Seed Button */}
              <button
                id="seed-btn"
                onClick={handleSeed}
                disabled={isSeeding}
                className="btn-primary px-4 sm:px-5 py-2.5 rounded-full text-[10px] uppercase tracking-widest disabled:opacity-50"
              >
                {isSeeding ? "Seeding..." : "Seed 33 Outcomes"}
              </button>
            </div>
          </div>
          <div className="live-line" />
        </header>

        {/* Main Content Area */}
        <main className="mt-32 px-4 sm:px-6 pb-24 max-w-[1380px] mx-auto w-full space-y-24">
          {/* Section 01: Active domain intelligence */}
          <section id="domain-intelligence" className="relative">
            <div className="absolute -top-12 right-0 mono-technical text-white/20">LIVE DATA / 01</div>
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4 mb-10">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <span className="mono-technical text-lime-300/70">01 /</span>
                  <span className="text-[10px] uppercase tracking-[.3em] text-white/35">
                    Signal architecture
                  </span>
                </div>
                <h2 className="serif-display text-4xl sm:text-6xl font-light">
                  Active domain <span className="italic text-lime-200">intelligence.</span>
                </h2>
              </div>
              <p className="max-w-xs text-sm text-white/40 leading-relaxed">
                Three live surfaces. One memory layer. Read the behavior before the agent acts.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Pitch Domain Card */}
              <article
                className="card domain-card domain-pitch accent-edge corner-mark p-6 sm:p-8"
                data-domain-card="pitch"
              >
                <div className="absolute top-0 left-10 right-10 h-px domain-line opacity-80" />
                <div className="flex items-start justify-between relative z-10">
                  <div>
                    <span className="mono-technical text-white/30">SURFACE / 01</span>
                    <h3 className="serif-display text-3xl mt-2" style={{ color: "var(--domain)" }}>
                      Pitch
                    </h3>
                  </div>
                  <button
                    onClick={() => fetchDomainBrief("pitch")}
                    aria-label="Refresh pitch brief"
                    className="text-white/35 hover:text-white transition-colors"
                  >
                    <iconify-icon icon="lucide:refresh-cw" />
                  </button>
                </div>

                <div className="flex items-center gap-6 mt-8 relative z-10">
                  <div className="relative w-28 h-28 shrink-0">
                    <svg viewBox="0 0 100 100" className="ring w-full h-full">
                      <circle cx="50" cy="50" r="40" className="ring-track" />
                      <circle
                        id="pitch-ring"
                        cx="50"
                        cy="50"
                        r="40"
                        className="ring-value"
                        style={{
                          strokeDashoffset: 251.2 - (251.2 * pitchPct) / 100,
                        }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <strong id="pitch-percent" className="serif-display text-2xl font-light">
                        {pitchPct}%
                      </strong>
                      <span className="text-[9px] uppercase text-white/35">confidence</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase tracking-widest text-white/35">
                      Outcomes observed
                    </span>
                    <div id="pitch-count" className="serif-display text-5xl font-light mt-1">
                      {pitchCount}
                    </div>
                    <p id="pitch-confidence" className="text-xs text-white/45 mt-1">
                      {pitchBrief.confidence || "Insufficient data"}
                    </p>
                  </div>
                </div>

                <div className="mt-8 grid grid-cols-3 gap-4 relative z-10">
                  <div className="flex gap-2">
                    <span
                      id="pitch-warning-bar"
                      className={`indicator ${pitchBrief.warning ? "red" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Warning</span>
                      <p id="pitch-warning" className="text-[11px] text-red-300 mt-1 line-clamp-3">
                        {pitchBrief.warning || "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span
                      id="pitch-pattern-bar"
                      className={`indicator ${pitchBrief.pattern ? "green" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Pattern</span>
                      <p id="pitch-pattern" className="text-[11px] text-lime-200 mt-1 line-clamp-3">
                        {pitchBrief.pattern || "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span
                      id="pitch-cross-bar"
                      className={`indicator ${pitchBrief.cross_domain ? "amber" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Cross</span>
                      <p id="pitch-cross" className="text-[11px] text-amber-200 mt-1 line-clamp-3">
                        {pitchBrief.cross_domain || "—"}
                      </p>
                    </div>
                  </div>
                </div>
              </article>

              {/* Post Domain Card */}
              <article
                className="card domain-card domain-post accent-edge corner-mark p-6 sm:p-8"
                data-domain-card="post"
              >
                <div className="absolute top-0 left-10 right-10 h-px domain-line opacity-80" />
                <div className="flex items-start justify-between relative z-10">
                  <div>
                    <span className="mono-technical text-white/30">SURFACE / 02</span>
                    <h3 className="serif-display text-3xl mt-2" style={{ color: "var(--domain)" }}>
                      Post
                    </h3>
                  </div>
                  <button
                    onClick={() => fetchDomainBrief("post")}
                    aria-label="Refresh post brief"
                    className="text-white/35 hover:text-white transition-colors"
                  >
                    <iconify-icon icon="lucide:refresh-cw" />
                  </button>
                </div>

                <div className="flex items-center gap-6 mt-8 relative z-10">
                  <div className="relative w-28 h-28 shrink-0">
                    <svg viewBox="0 0 100 100" className="ring w-full h-full">
                      <circle cx="50" cy="50" r="40" className="ring-track" />
                      <circle
                        id="post-ring"
                        cx="50"
                        cy="50"
                        r="40"
                        className="ring-value"
                        style={{
                          strokeDashoffset: 251.2 - (251.2 * postPct) / 100,
                        }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <strong id="post-percent" className="serif-display text-2xl font-light">
                        {postPct}%
                      </strong>
                      <span className="text-[9px] uppercase text-white/35">confidence</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase tracking-widest text-white/35">
                      Outcomes observed
                    </span>
                    <div id="post-count" className="serif-display text-5xl font-light mt-1">
                      {postCount}
                    </div>
                    <p id="post-confidence" className="text-xs text-white/45 mt-1">
                      {postBrief.confidence || "Insufficient data"}
                    </p>
                  </div>
                </div>

                <div className="mt-8 grid grid-cols-3 gap-4 relative z-10">
                  <div className="flex gap-2">
                    <span
                      id="post-warning-bar"
                      className={`indicator ${postBrief.warning ? "red" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Warning</span>
                      <p id="post-warning" className="text-[11px] text-red-300 mt-1 line-clamp-3">
                        {postBrief.warning || "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span
                      id="post-pattern-bar"
                      className={`indicator ${postBrief.pattern ? "green" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Pattern</span>
                      <p id="post-pattern" className="text-[11px] text-lime-200 mt-1 line-clamp-3">
                        {postBrief.pattern || "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span
                      id="post-cross-bar"
                      className={`indicator ${postBrief.cross_domain ? "amber" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Cross</span>
                      <p id="post-cross" className="text-[11px] text-amber-200 mt-1 line-clamp-3">
                        {postBrief.cross_domain || "—"}
                      </p>
                    </div>
                  </div>
                </div>
              </article>

              {/* Ask Domain Card */}
              <article
                className="card domain-card domain-ask accent-edge corner-mark p-6 sm:p-8"
                data-domain-card="ask"
              >
                <div className="absolute top-0 left-10 right-10 h-px domain-line opacity-80" />
                <div className="flex items-start justify-between relative z-10">
                  <div>
                    <span className="mono-technical text-white/30">SURFACE / 03</span>
                    <h3 className="serif-display text-3xl mt-2" style={{ color: "var(--domain)" }}>
                      Ask
                    </h3>
                  </div>
                  <button
                    onClick={() => fetchDomainBrief("ask")}
                    aria-label="Refresh ask brief"
                    className="text-white/35 hover:text-white transition-colors"
                  >
                    <iconify-icon icon="lucide:refresh-cw" />
                  </button>
                </div>

                <div className="flex items-center gap-6 mt-8 relative z-10">
                  <div className="relative w-28 h-28 shrink-0">
                    <svg viewBox="0 0 100 100" className="ring w-full h-full">
                      <circle cx="50" cy="50" r="40" className="ring-track" />
                      <circle
                        id="ask-ring"
                        cx="50"
                        cy="50"
                        r="40"
                        className="ring-value"
                        style={{
                          strokeDashoffset: 251.2 - (251.2 * askPct) / 100,
                        }}
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <strong id="ask-percent" className="serif-display text-2xl font-light">
                        {askPct}%
                      </strong>
                      <span className="text-[9px] uppercase text-white/35">confidence</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-[10px] uppercase tracking-widest text-white/35">
                      Outcomes observed
                    </span>
                    <div id="ask-count" className="serif-display text-5xl font-light mt-1">
                      {askCount}
                    </div>
                    <p id="ask-confidence" className="text-xs text-white/45 mt-1">
                      {askBrief.confidence || "Insufficient data"}
                    </p>
                  </div>
                </div>

                <div className="mt-8 grid grid-cols-3 gap-4 relative z-10">
                  <div className="flex gap-2">
                    <span
                      id="ask-warning-bar"
                      className={`indicator ${askBrief.warning ? "red" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Warning</span>
                      <p id="ask-warning" className="text-[11px] text-red-300 mt-1 line-clamp-3">
                        {askBrief.warning || "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span
                      id="ask-pattern-bar"
                      className={`indicator ${askBrief.pattern ? "green" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Pattern</span>
                      <p id="ask-pattern" className="text-[11px] text-lime-200 mt-1 line-clamp-3">
                        {askBrief.pattern || "—"}
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <span
                      id="ask-cross-bar"
                      className={`indicator ${askBrief.cross_domain ? "amber" : ""}`}
                    />
                    <div>
                      <span className="text-[9px] uppercase text-white/35">Cross</span>
                      <p id="ask-cross" className="text-[11px] text-amber-200 mt-1 line-clamp-3">
                        {askBrief.cross_domain || "—"}
                      </p>
                    </div>
                  </div>
                </div>
              </article>
            </div>
          </section>

          {/* Section 02: Memory Inspector */}
          <section id="memory-inspector" className="relative">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-5 mb-8">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <span className="mono-technical text-lime-300/70">02 /</span>
                  <span className="text-[10px] uppercase tracking-[.3em] text-white/35">
                    The file, exposed
                  </span>
                </div>
                <h2 className="serif-display text-4xl sm:text-5xl font-light">
                  Memory <span className="italic">inspector.</span>
                </h2>
              </div>
              <div className="flex p-1 rounded-full bg-white/[.04] border border-white/10">
                <button
                  onClick={() => setActiveTab("cold")}
                  id="tab-cold"
                  className={`tab px-5 py-2.5 rounded-full text-[10px] uppercase tracking-widest font-bold flex items-center gap-2 ${
                    activeTab === "cold" ? "tab-active" : "text-white/40"
                  }`}
                >
                  <iconify-icon icon="lucide:database" /> Cold Journal
                </button>
                <button
                  onClick={() => setActiveTab("warm")}
                  id="tab-warm"
                  className={`tab px-5 py-2.5 rounded-full text-[10px] uppercase tracking-widest font-bold flex items-center gap-2 ${
                    activeTab === "warm" ? "tab-active" : "text-white/40"
                  }`}
                >
                  <iconify-icon icon="lucide:sparkles" /> Warm Patterns
                </button>
              </div>
            </div>

            <div className="card accent-edge overflow-hidden">
              {/* Cold Journal Tab */}
              {activeTab === "cold" && (
                <div id="cold-view" className="p-5 sm:p-8">
                  <div className="flex items-center justify-between mb-5">
                    <span className="mono-technical text-white/30">COLD / APPEND-ONLY JOURNAL</span>
                    <span className="text-[10px] text-lime-300/60 uppercase tracking-widest">
                      {loadingEvents ? "Loading..." : "Auto-refresh 10s"}
                    </span>
                  </div>
                  <div className="overflow-x-auto scroll-custom max-h-[430px]">
                    <table className="w-full min-w-[720px] text-left">
                      <thead>
                        <tr className="text-[10px] uppercase text-white/30 border-b border-white/10">
                          <th className="pb-4 font-normal">Timestamp</th>
                          <th className="pb-4 font-normal">User</th>
                          <th className="pb-4 font-normal">Domain</th>
                          <th className="pb-4 font-normal">Signal</th>
                          <th className="pb-4 font-normal">Action</th>
                          <th className="pb-4 font-normal">Outcome</th>
                        </tr>
                      </thead>
                      <tbody id="events-list" className="divide-y divide-white/5">
                        {events.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="py-14 text-center text-white/25 italic">
                              Journal empty. No historical events stored.
                            </td>
                          </tr>
                        ) : (
                          events.map((ev, idx) => {
                            const isWin = ev.signal === 1;
                            const isLoss = ev.signal === -1;
                            const sigColor = isWin
                              ? "text-lime-300"
                              : isLoss
                              ? "text-red-300"
                              : "text-white/45";
                            const sigIcon = isWin
                              ? "lucide:check-circle"
                              : isLoss
                              ? "lucide:alert-circle"
                              : "lucide:circle";

                            return (
                              <tr key={idx} className="row-hover text-xs border-b border-white/5">
                                <td className="py-4 mono-technical text-white/30">
                                  {ev.timestamp || ev.created_at || "Recent"}
                                </td>
                                <td className="py-4 text-white/60">
                                  {(ev.user_id || "alex").split(":").pop()}
                                </td>
                                <td className="py-4">
                                  <span className="bg-white/5 px-2 py-1 rounded text-[10px] uppercase font-bold text-white/65">
                                    {ev.domain}
                                  </span>
                                </td>
                                <td className={`py-4 ${sigColor} font-bold`}>
                                  <span className="inline-flex items-center gap-1">
                                    <iconify-icon icon={sigIcon} />
                                    {ev.signal > 0 ? `+${ev.signal}` : ev.signal}
                                  </span>
                                </td>
                                <td className="py-4 text-white/70 italic">{ev.action}</td>
                                <td className="py-4 text-white/90">{ev.outcome}</td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Warm Patterns Tab */}
              {activeTab === "warm" && (
                <div id="warm-view" className="p-5 sm:p-8">
                  <div className="flex items-center justify-between mb-6">
                    <span className="mono-technical text-white/30">WARM / DERIVED ENTITIES</span>
                    <span className="text-[10px] text-violet-300/60 uppercase tracking-widest">
                      {loadingPatterns ? "Recalculating..." : "Recalculated live"}
                    </span>
                  </div>
                  <div id="patterns-grid" className="grid grid-cols-1 md:grid-cols-3 gap-5">
                    {patterns.length === 0 ? (
                      <div className="col-span-full py-16 text-center text-white/25 italic">
                        No patterns formed yet. Record more outcomes or click &quot;Seed 33 Outcomes&quot;.
                      </div>
                    ) : (
                      patterns.map((p, idx) => {
                        const winPct = Math.round((p.win_rate || 0) * 100);
                        const lossPct = Math.round((p.loss_rate || 0) * 100);
                        return (
                          <div
                            key={idx}
                            className="card p-5 bg-gradient-to-br from-white/[.08] to-transparent border border-white/10 rounded-2xl"
                          >
                            <div className="flex justify-between items-center mb-5">
                              <h4 className="text-xs uppercase tracking-widest font-bold text-lime-300">
                                {p.domain}
                              </h4>
                              <span className="mono-technical text-white/35">
                                Avg {Number(p.avg_signal || 0).toFixed(2)}
                              </span>
                            </div>
                            <div className="flex items-center gap-5">
                              <div className="relative w-20 h-20 shrink-0">
                                <svg viewBox="0 0 100 100" className="ring w-full h-full">
                                  <circle cx="50" cy="50" r="40" className="ring-track" />
                                  <circle
                                    cx="50"
                                    cy="50"
                                    r="40"
                                    className="ring-value"
                                    style={{
                                      stroke: "var(--acid-lime)",
                                      strokeDashoffset: 251.2 - (251.2 * winPct) / 100,
                                    }}
                                  />
                                </svg>
                                <span className="absolute inset-0 flex items-center justify-center text-sm font-bold">
                                  {winPct}%
                                </span>
                              </div>
                              <div className="space-y-2 text-xs">
                                <span className="inline-block px-2.5 py-1 rounded-full bg-lime-400/15 text-lime-300 mr-2">
                                  Win {winPct}%
                                </span>
                                <span className="inline-block px-2.5 py-1 rounded-full bg-red-400/15 text-red-300">
                                  Loss {lossPct}%
                                </span>
                              </div>
                            </div>
                            <div className="mt-5 space-y-2">
                              <span className="text-[9px] uppercase tracking-widest text-white/30">
                                Recent wins
                              </span>
                              <p className="text-xs text-white/65">
                                {(p.recent_wins || []).slice(0, 2).join(" · ") || "None yet"}
                              </p>
                              <span className="text-[9px] uppercase tracking-widest text-white/30 block pt-2">
                                Recent losses
                              </span>
                              <p className="text-xs text-white/65">
                                {(p.recent_losses || []).slice(0, 2).join(" · ") || "None yet"}
                              </p>
                            </div>
                            <div className="mono-technical text-[10px] text-white/25 mt-5">
                              {p.last_calculated || "Awaiting calculation"}
                            </div>
                          </div>
                        );
                      })
                    )}
                  </div>
                </div>
              )}
            </div>
          </section>

          {/* Section 03: Outcome Recorder */}
          <section id="outcome-recorder" className="relative">
            <div className="flex items-center gap-3 mb-8">
              <span className="mono-technical text-lime-300/70">03 /</span>
              <h2 className="serif-display text-4xl sm:text-5xl font-light">
                Outcome <span className="italic">recorder.</span>
              </h2>
            </div>

            <div className="card accent-edge p-5 sm:p-9 overflow-hidden">
              <div className="absolute inset-0 dots-field opacity-20 pointer-events-none" />

              {/* Toast message */}
              {showToast && (
                <div
                  id="record-toast"
                  className="absolute top-6 right-6 z-20 bg-lime-300 text-stone-950 px-4 py-2 rounded-full font-bold text-sm shadow-xl"
                >
                  ✓ Recorded — memory updated
                </div>
              )}

              {/* Retrieved Brief Box if requested */}
              {recorderBrief && (
                <div className="relative z-10 mb-8 p-4 rounded-2xl bg-white/[.04] border border-lime-300/30">
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-[10px] uppercase tracking-widest text-lime-300 font-bold">
                      Retrieved Memory Brief ({selectedDomain})
                    </span>
                    <span className="text-xs text-white/40">{recorderBrief.confidence}</span>
                  </div>
                  <div className="grid sm:grid-cols-3 gap-3 text-xs">
                    <div>
                      <span className="text-[9px] uppercase text-white/30 block">Warning</span>
                      <p className="text-red-300 mt-0.5">{recorderBrief.warning || "None detected"}</p>
                    </div>
                    <div>
                      <span className="text-[9px] uppercase text-white/30 block">Pattern</span>
                      <p className="text-lime-200 mt-0.5">{recorderBrief.pattern || "None detected"}</p>
                    </div>
                    <div>
                      <span className="text-[9px] uppercase text-white/30 block">Cross Domain</span>
                      <p className="text-amber-200 mt-0.5">{recorderBrief.cross_domain || "None detected"}</p>
                    </div>
                  </div>
                </div>
              )}

              <div className="relative z-10 grid grid-cols-1 lg:grid-cols-2 gap-10">
                <div className="lg:border-r border-white/10 lg:pr-10 space-y-7">
                  <div>
                    <label className="text-[10px] uppercase tracking-[.25em] text-white/40 block mb-3">
                      Choose the surface
                    </label>
                    <div className="flex flex-wrap gap-2">
                      {(["pitch", "post", "ask"] as const).map((d) => {
                        const active = selectedDomain === d;
                        return (
                          <button
                            key={d}
                            onClick={() => setSelectedDomain(d)}
                            data-domain={d}
                            className={`domain-pill px-5 py-2.5 rounded-full border text-xs font-semibold capitalize transition-all ${
                              active
                                ? "bg-lime-300 text-stone-950 border-lime-300 shadow-lg shadow-lime-300/20"
                                : "border-white/10 text-white/70 hover:border-white/30"
                            }`}
                          >
                            {d}
                          </button>
                        );
                      })}
                    </div>
                  </div>

                  <div>
                    <label className="text-[10px] uppercase tracking-[.25em] text-white/40 block mb-3">
                      Context
                    </label>
                    <textarea
                      id="record-context"
                      value={recordContext}
                      onChange={(e) => setRecordContext(e.target.value)}
                      className="field w-full rounded-2xl p-4 text-sm h-36 resize-none"
                      placeholder="What are you about to do?"
                    />
                  </div>

                  <button
                    onClick={handleGetBriefForRecorder}
                    disabled={isGettingBrief}
                    className="w-full py-4 rounded-full border border-lime-300/70 text-lime-200 text-[10px] font-bold uppercase tracking-[.2em] hover:bg-lime-300 hover:text-stone-950 transition-all disabled:opacity-50"
                  >
                    {isGettingBrief ? "Retrieving..." : "Get Brief Before Acting"}{" "}
                    <iconify-icon icon="lucide:arrow-up-right" class="ml-1 inline" />
                  </button>
                </div>

                <div className="space-y-6">
                  <div>
                    <label className="text-[10px] uppercase tracking-[.25em] text-white/40 block mb-3">
                      Action taken
                    </label>
                    <input
                      id="record-action"
                      type="text"
                      value={recordAction}
                      onChange={(e) => setRecordAction(e.target.value)}
                      className="field w-full rounded-full px-5 py-3.5 text-sm"
                      placeholder="What did you do?"
                    />
                  </div>

                  <div>
                    <label className="text-[10px] uppercase tracking-[.25em] text-white/40 block mb-3">
                      Observed outcome
                    </label>
                    <input
                      id="record-outcome"
                      type="text"
                      value={recordOutcome}
                      onChange={(e) => setRecordOutcome(e.target.value)}
                      className="field w-full rounded-full px-5 py-3.5 text-sm"
                      placeholder="What happened?"
                    />
                  </div>

                  <div>
                    <label className="text-[10px] uppercase tracking-[.25em] text-white/40 block mb-3">
                      Signal strength
                    </label>
                    <div className="flex gap-3">
                      <button
                        onClick={() => setActiveSignal(-1)}
                        data-signal="-1"
                        className={`signal-btn flex-1 py-3 rounded-full border text-sm font-bold transition-all ${
                          activeSignal === -1
                            ? "bg-red-500 text-white border-red-400 shadow-lg shadow-red-500/30"
                            : "border-red-900/40 text-red-300 bg-red-950/20"
                        }`}
                      >
                        −1
                      </button>
                      <button
                        onClick={() => setActiveSignal(0)}
                        data-signal="0"
                        className={`signal-btn flex-1 py-3 rounded-full border text-sm font-bold transition-all ${
                          activeSignal === 0
                            ? "bg-white text-stone-950 border-white shadow-lg"
                            : "border-white/10 text-white/45 bg-white/[.04]"
                        }`}
                      >
                        0
                      </button>
                      <button
                        onClick={() => setActiveSignal(1)}
                        data-signal="1"
                        className={`signal-btn flex-1 py-3 rounded-full border text-sm font-bold transition-all ${
                          activeSignal === 1
                            ? "bg-lime-300 text-stone-950 border-lime-300 shadow-lg shadow-lime-300/30"
                            : "border-lime-900/40 text-lime-300 bg-lime-950/20"
                        }`}
                      >
                        +1
                      </button>
                    </div>
                  </div>

                  <button
                    onClick={handleSubmitOutcome}
                    disabled={isSubmittingOutcome}
                    className="btn-primary w-full py-4 rounded-full text-[10px] uppercase tracking-[.2em] disabled:opacity-50"
                  >
                    {isSubmittingOutcome ? "Recording..." : "Record Outcome"}{" "}
                    <iconify-icon icon="lucide:arrow-right" class="ml-1 inline" />
                  </button>
                </div>
              </div>
            </div>
          </section>

          {/* Section 04: Watch Lumen Learn */}
          <section id="watch-learn" className="relative">
            <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-5 mb-9">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <span className="mono-technical text-lime-300/70">04 /</span>
                  <span className="text-[10px] uppercase tracking-[.3em] text-white/35">
                    Behavioral fork
                  </span>
                </div>
                <h2 className="serif-display text-4xl sm:text-5xl font-light">
                  Watch Lumen <span className="italic">learn.</span>
                </h2>
                <p className="text-white/45 mt-3 max-w-lg leading-relaxed">
                  A five-step sequence. Each action writes memory, recalculates patterns, and changes what the agent sees next.
                </p>
              </div>
              <div className="flex gap-3">
                <button
                  onClick={handleResetDemo}
                  className="px-5 py-2.5 rounded-full border border-white/10 text-[10px] uppercase tracking-widest hover:bg-white/5 transition-all"
                >
                  ↺ Reset
                </button>
                <button
                  id="demo-step-btn"
                  onClick={handleRunNextStep}
                  disabled={currentDemoStep >= 5 || isStepRunning}
                  className={`btn-primary px-6 py-2.5 rounded-full text-[10px] uppercase tracking-widest ${
                    currentDemoStep >= 5 ? "opacity-40 cursor-not-allowed" : ""
                  }`}
                >
                  {isStepRunning
                    ? "Running..."
                    : currentDemoStep >= 5
                    ? "Sequence Complete"
                    : "▶ Run Next Step"}
                </button>
              </div>
            </div>

            <div className="card accent-edge p-6 sm:p-10 relative overflow-hidden">
              <div className="absolute inset-0 grid-field opacity-40 pointer-events-none" />
              <div className="relative max-w-4xl mx-auto">
                <div className="timeline-line absolute left-1/2 top-5 bottom-5 w-px -translate-x-1/2 hidden md:block" />
                <div id="timeline-list" className="space-y-6">
                  {TIMELINE_STEPS.map((s, i) => {
                    const stepNum = i + 1;
                    const state =
                      currentDemoStep >= stepNum
                        ? "done"
                        : currentDemoStep === stepNum - 1
                        ? "current"
                        : "";

                    return (
                      <div
                        key={i}
                        className={`relative flex items-center gap-5 md:gap-10 ${
                          i % 2 ? "md:flex-row-reverse" : ""
                        }`}
                      >
                        <div
                          className={`timeline-node ${state} shrink-0 md:absolute md:left-1/2 md:-translate-x-1/2`}
                        />
                        <div
                          className={`step-card ${
                            state === "current" ? "current" : ""
                          } card p-5 md:w-[44%] ${i % 2 ? "md:mr-auto" : "md:ml-auto"}`}
                        >
                          <div className="flex items-center justify-between mb-2">
                            <span className="mono-technical text-lime-300/70">
                              STEP 0{stepNum}
                            </span>
                            <span
                              className={`text-[9px] uppercase tracking-widest ${
                                state === "done"
                                  ? "text-lime-300"
                                  : state === "current"
                                  ? "text-lime-200"
                                  : "text-white/25"
                              }`}
                            >
                              {state === "done" ? "Complete" : state === "current" ? "Now" : "Queued"}
                            </span>
                          </div>
                          <h4 className="serif-display text-2xl font-light">{s.name}</h4>
                          <p className="text-xs text-white/45 mt-1">{s.desc}</p>
                          <code className="mono-technical text-lime-300/75 block mt-4 text-[11px]">
                            {state === "done" || state === "current"
                              ? s.action
                              : "// awaiting memory event"}
                          </code>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </div>
          </section>

          {/* Section 05: Danger Zone */}
          <section id="danger-zone">
            <div className="card danger p-6 sm:p-9 flex flex-col md:flex-row items-center justify-between gap-8 overflow-hidden relative">
              <div className="absolute inset-0 grid-field opacity-20 pointer-events-none" />
              <div className="relative z-10 flex items-center gap-6">
                <div className="w-20 h-20 rounded-3xl bg-gradient-to-br from-red-500/20 to-orange-500/10 border border-red-500/30 flex items-center justify-center shrink-0">
                  <iconify-icon icon="lucide:flame" class="danger-icon text-orange-400 text-4xl" />
                </div>
                <div>
                  <div className="flex items-center gap-2 mb-2">
                    <iconify-icon icon="lucide:alert-triangle" class="text-red-400" />
                    <span className="text-[10px] font-bold uppercase tracking-[.25em] text-red-400">
                      Load-bearing delete test
                    </span>
                  </div>
                  <h3 className="serif-display text-2xl sm:text-3xl">
                    Delete the memory. Watch the intelligence disappear.
                  </h3>
                  <p className="text-sm text-white/45 mt-2 max-w-xl leading-relaxed">
                    Permanently remove the Sibyl memory file. This is the empirical proof that Lumen is not a decorative logging layer.
                  </p>
                </div>
              </div>
              <button
                onClick={handleConfirmWipe}
                className="wipe-button relative z-10 shrink-0 text-[10px] uppercase tracking-widest font-bold flex items-center justify-center text-center"
              >
                Wipe
                <br />
                Memory
              </button>
            </div>
          </section>
        </main>

        {/* Footer */}
        <footer className="border-t border-white/10 bg-gradient-to-b from-[#171412] to-[#0C0A09] px-6 py-12">
          <div className="max-w-[1380px] mx-auto grid grid-cols-1 md:grid-cols-4 gap-10 items-start">
            <div className="md:col-span-2">
              <Link href="/" id="footer-logo-link" className="inline-flex items-center gap-3">
                <div className="w-9 h-9 rounded-xl bg-lime-300 text-stone-950 flex items-center justify-center">
                  <iconify-icon icon="lucide:brain-circuit" />
                </div>
                <span className="serif-display text-2xl italic">Lumen</span>
              </Link>
              <p className="text-sm text-white/35 mt-5 max-w-sm">
                Outcome memory for agents that learn from what actually happened.
              </p>
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-[.25em] text-white/25">System</span>
              <div className="mt-4 space-y-2 text-sm text-white/50">
                <a href="#domain-intelligence" id="footer-intelligence-link" className="block hover:text-lime-300 transition-colors">
                  Intelligence
                </a>
                <a href="#memory-inspector" id="footer-inspector-link" className="block hover:text-lime-300 transition-colors">
                  Memory inspector
                </a>
                <a href="#watch-learn" id="footer-learn-link" className="block hover:text-lime-300 transition-colors">
                  Watch Lumen learn
                </a>
              </div>
            </div>
            <div>
              <span className="text-[10px] uppercase tracking-[.25em] text-white/25">Infrastructure</span>
              <div className="mt-4 space-y-3 text-sm text-white/50">
                <a
                  href="https://github.com/Sibyl-Labs/lumen"
                  target="_blank"
                  rel="noopener noreferrer"
                  id="footer-gh-link"
                  className="flex items-center gap-2 hover:text-lime-300 transition-colors"
                >
                  <iconify-icon icon="mdi:github" /> GitHub
                </a>
                <span className="flex items-center gap-2">
                  <iconify-icon icon="lucide:cpu" /> Powered by Sibyl Memory
                </span>
                <span className="flex items-center gap-2">
                  <iconify-icon icon="lucide:coins" /> Built on Base
                </span>
              </div>
            </div>
          </div>
          <div className="max-w-[1380px] mx-auto mt-12 pt-5 border-t border-white/10 flex flex-col sm:flex-row justify-between gap-3 text-[10px] text-white/25 uppercase tracking-widest">
            <span>© 2026 Lumen Protocol</span>
            <span className="mono-technical normal-case tracking-normal">
              API: lumen-memory-production.up.railway.app
            </span>
          </div>
        </footer>
      </div>
    </div>
  );
}
