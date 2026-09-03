"use client";

import React, { useEffect, useState, useCallback } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { BriefCard, BriefData } from "@/components/BriefCard";
import { OutcomeRecorder } from "@/components/OutcomeRecorder";
import { DemoRunner } from "@/components/DemoRunner";
import { WipePanel } from "@/components/WipePanel";
import { Database, Sparkles, RefreshCw } from "lucide-react";

const API_BASE = "http://localhost:8000";
const DEMO_KEY = "lmn_demo0000000000000000000000000000";

export default function ConsolePage() {
  const [pitchBrief, setPitchBrief] = useState<BriefData | null>(null);
  const [postBrief, setPostBrief] = useState<BriefData | null>(null);
  const [askBrief, setAskBrief] = useState<BriefData | null>(null);

  const [loadingPitch, setLoadingPitch] = useState(false);
  const [loadingPost, setLoadingPost] = useState(false);
  const [loadingAsk, setLoadingAsk] = useState(false);

  const [selectedDomain, setSelectedDomain] = useState<"pitch" | "post" | "ask">("pitch");
  const [isApiOnline, setIsApiOnline] = useState(true);
  const [isSeeding, setIsSeeding] = useState(false);

  // Demo Runner states
  const [demoStep, setDemoStep] = useState(0);
  const [stepLabel, setStepLabel] = useState("");
  const [actionTaken, setActionTaken] = useState("");

  const fetchBriefForDomain = useCallback(
    async (domain: "pitch" | "post" | "ask", context: string = "") => {
      const setLoading =
        domain === "pitch"
          ? setLoadingPitch
          : domain === "post"
          ? setLoadingPost
          : setLoadingAsk;

      const setBrief =
        domain === "pitch"
          ? setPitchBrief
          : domain === "post"
          ? setPostBrief
          : setAskBrief;

      setLoading(true);
      try {
        const res = await fetch(`${API_BASE}/brief`, {
          method: "POST",
          headers: { 
            "Content-Type": "application/json",
            "X-Lumen-Key": DEMO_KEY,
          },
          body: JSON.stringify({
            user_id: "alex",
            domain,
            context,
          }),
        });
        if (!res.ok) throw new Error("API error");
        const data = (await res.json()) as BriefData;
        setBrief(data);
        setIsApiOnline(true);
        return data;
      } catch {
        setIsApiOnline(false);
        return null;
      } finally {
        setLoading(false);
      }
    },
    []
  );

  const refreshAllBriefs = useCallback(async () => {
    await Promise.all([
      fetchBriefForDomain("pitch"),
      fetchBriefForDomain("post"),
      fetchBriefForDomain("ask"),
    ]);
  }, [fetchBriefForDomain]);

  useEffect(() => {
    refreshAllBriefs();
  }, [refreshAllBriefs]);

  // Total outcomes calculation
  const totalOutcomes =
    (pitchBrief?.raw_outcomes || 0) +
    (postBrief?.raw_outcomes || 0) +
    (askBrief?.raw_outcomes || 0);

  // Quick Seed Handler
  const handleQuickSeed = async () => {
    setIsSeeding(true);
    try {
      const res = await fetch(`${API_BASE}/seed`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-Lumen-Key": DEMO_KEY,
        },
        body: JSON.stringify({}),
      });
      if (!res.ok) throw new Error("Seed failed");
      setDemoStep(1);
      setStepLabel("Session 1 — Memory loaded from Sibyl");
      setActionTaken("Seeded 33 outcomes into Sibyl memory");
      await refreshAllBriefs();
    } catch (err) {
      console.error("Seed error", err);
    } finally {
      setIsSeeding(false);
    }
  };

  // Handler for Recording Outcome
  const handleRecordOutcome = async (
    domain: "pitch" | "post" | "ask",
    action: string,
    outcome: string,
    signal: number
  ) => {
    const res = await fetch(`${API_BASE}/record`, {
      method: "POST",
      headers: { 
        "Content-Type": "application/json",
        "X-Lumen-Key": DEMO_KEY,
      },
      body: JSON.stringify({
        user_id: "alex",
        domain,
        action,
        outcome,
        signal,
      }),
    });
    if (!res.ok) throw new Error("Failed to record outcome");
    await refreshAllBriefs();
  };

  // Handler for Demo Step Runner
  const handleRunStep = async (step: number) => {
    try {
      const res = await fetch(`${API_BASE}/demo/step`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-Lumen-Key": DEMO_KEY,
        },
        body: JSON.stringify({ step }),
      });
      if (!res.ok) throw new Error("Step execution failed");
      const data = await res.json();
      setDemoStep(data.step);
      setStepLabel(data.step_label);
      setActionTaken(data.action_taken);
      setPitchBrief(data.brief);
      await Promise.all([fetchBriefForDomain("post"), fetchBriefForDomain("ask")]);
      return data.brief;
    } catch (err) {
      console.error("Error running demo step", err);
      return null;
    }
  };

  // Handler for Reset Demo
  const handleResetDemo = async () => {
    try {
      const res = await fetch(`${API_BASE}/demo/step`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-Lumen-Key": DEMO_KEY,
        },
        body: JSON.stringify({ step: 5 }),
      });
      if (!res.ok) throw new Error("Reset failed");
      const data = await res.json();
      setDemoStep(0);
      setStepLabel(data.step_label);
      setActionTaken(data.action_taken);
      await refreshAllBriefs();
      return data.brief;
    } catch (err) {
      console.error("Error resetting demo", err);
      return null;
    }
  };

  // Handler for Wipe Memory
  const handleWipeMemory = async () => {
    try {
      const res = await fetch(`${API_BASE}/wipe`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          "X-Lumen-Key": DEMO_KEY,
        },
        body: JSON.stringify({}),
      });
      if (!res.ok) throw new Error("Wipe failed");
      setDemoStep(4);
      setStepLabel("Session After Wipe — Memory deleted, agent blind");
      setActionTaken("Deleted ~/.sibyl-memory/lumen_demo.db");
      await refreshAllBriefs();
    } catch (err) {
      console.error("Error wiping memory", err);
    }
  };

  return (
    <div className="min-h-screen bg-canvas text-text-primary selection:bg-brand-500 selection:text-white flex flex-col justify-between">
      <div>
        <Navbar />

        <main className="max-w-6xl mx-auto px-4 sm:px-6 py-10 space-y-8">
          {/* Header */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between pb-6 border-b border-border-subtle gap-4">
            <div>
              <div className="flex items-center gap-3">
                <h1 className="text-2xl font-bold tracking-tight text-white">
                  Lumen Live Console
                </h1>
                <span className="bg-surface-2 text-indigo-300 text-[11px] font-mono font-medium px-2.5 py-0.5 rounded border border-border-muted">
                  Sibyl Local Substrate
                </span>
              </div>
              <p className="text-xs text-text-secondary mt-1">
                Real-time outcome recording and pattern briefing for user{" "}
                <span className="text-white font-mono font-semibold">&quot;alex&quot;</span>
              </p>
            </div>

            {/* Actions & Status */}
            <div className="flex items-center gap-3">
              <button
                onClick={handleQuickSeed}
                disabled={isSeeding}
                className="bg-surface-2 hover:bg-surface-3 border border-border-muted text-xs font-mono font-medium text-text-secondary hover:text-white px-3 py-1.5 rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
              >
                <Sparkles className="w-3.5 h-3.5 text-amber-400" />
                <span>{isSeeding ? "Seeding..." : "Seed Baseline (33)"}</span>
              </button>

              {/* Live Status Indicator */}
              <div className="flex items-center gap-2 bg-surface-1 border border-border-subtle px-3 py-1.5 rounded-lg shadow-xs font-mono text-xs">
                {!isApiOnline ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-amber-500 animate-pulse" />
                    <span className="text-amber-400">API OFFLINE</span>
                  </>
                ) : totalOutcomes > 0 ? (
                  <>
                    <span className="w-2 h-2 rounded-full bg-emerald-500" />
                    <span className="text-emerald-300">
                      MEMORY ACTIVE ({totalOutcomes})
                    </span>
                  </>
                ) : (
                  <>
                    <span className="w-2 h-2 rounded-full bg-rose-500" />
                    <span className="text-rose-400">MEMORY EMPTY</span>
                  </>
                )}
              </div>
            </div>
          </div>

          {/* Section 1: Three Brief Panels */}
          <section className="space-y-3">
            <div className="flex items-center justify-between">
              <h2 className="text-xs font-bold uppercase tracking-wider text-text-muted font-mono flex items-center gap-2">
                <Database className="w-3.5 h-3.5 text-indigo-400" />
                Active Domain Intelligence
              </h2>
              <button
                onClick={refreshAllBriefs}
                className="text-xs text-indigo-400 hover:text-indigo-300 font-mono transition-colors flex items-center gap-1"
              >
                <RefreshCw className="w-3 h-3" />
                <span>Refresh All</span>
              </button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <BriefCard
                domain="pitch"
                data={pitchBrief}
                loading={loadingPitch}
                onRefresh={() => fetchBriefForDomain("pitch")}
              />
              <BriefCard
                domain="post"
                data={postBrief}
                loading={loadingPost}
                onRefresh={() => fetchBriefForDomain("post")}
              />
              <BriefCard
                domain="ask"
                data={askBrief}
                loading={loadingAsk}
                onRefresh={() => fetchBriefForDomain("ask")}
              />
            </div>
          </section>

          {/* Section 2: Outcome Recorder */}
          <section>
            <OutcomeRecorder
              selectedDomain={selectedDomain}
              onSelectDomain={(d) => setSelectedDomain(d)}
              onGetBrief={(d, ctx) => fetchBriefForDomain(d, ctx)}
              onRecordOutcome={handleRecordOutcome}
            />
          </section>

          {/* Section 3: Run Demo */}
          <section>
            <DemoRunner
              currentStep={demoStep}
              stepLabel={stepLabel}
              actionTaken={actionTaken}
              onRunStep={handleRunStep}
              onReset={handleResetDemo}
            />
          </section>

          {/* Section 4: Wipe Panel */}
          <section>
            <WipePanel onWipe={handleWipeMemory} />
          </section>
        </main>
      </div>

      <Footer />
    </div>
  );
}
