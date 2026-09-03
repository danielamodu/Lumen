"use client";

import React, { useState } from "react";
import { Send, Check, Search, PlusCircle } from "lucide-react";

interface OutcomeRecorderProps {
  selectedDomain: "pitch" | "post" | "ask";
  onSelectDomain: (domain: "pitch" | "post" | "ask") => void;
  onGetBrief: (domain: "pitch" | "post" | "ask", context: string) => Promise<unknown>;
  onRecordOutcome: (
    domain: "pitch" | "post" | "ask",
    action: string,
    outcome: string,
    signal: number
  ) => Promise<void>;
}

export const OutcomeRecorder: React.FC<OutcomeRecorderProps> = ({
  selectedDomain,
  onSelectDomain,
  onGetBrief,
  onRecordOutcome,
}) => {
  const [context, setContext] = useState("");
  const [action, setAction] = useState("");
  const [outcome, setOutcome] = useState("");
  const [signal, setSignal] = useState<number>(1);
  const [isGettingBrief, setIsGettingBrief] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [recordedSuccess, setRecordedSuccess] = useState(false);
  const [validationError, setValidationError] = useState<string | null>(null);

  const handleGetBrief = async () => {
    setIsGettingBrief(true);
    try {
      await onGetBrief(selectedDomain, context);
    } finally {
      setIsGettingBrief(false);
    }
  };

  const handleRecord = async () => {
    if (!action.trim() || !outcome.trim()) {
      setValidationError("Please provide both an action and an outcome.");
      return;
    }
    setValidationError(null);
    setIsRecording(true);
    try {
      await onRecordOutcome(selectedDomain, action.trim(), outcome.trim(), signal);
      setRecordedSuccess(true);
      setAction("");
      setOutcome("");
      setTimeout(() => {
        setRecordedSuccess(false);
      }, 2000);
    } catch {
      setValidationError("Failed to record outcome. Is the API server running?");
    } finally {
      setIsRecording(false);
    }
  };

  return (
    <div className="bg-surface-1 rounded-xl border border-border-subtle p-6 shadow-card">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Left Side: Context & Get Brief */}
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-semibold text-white flex items-center gap-2">
              <Search className="w-4 h-4 text-indigo-400" />
              Context & Session Query
            </h3>
            {/* Domain Selector Pills */}
            <div className="flex items-center bg-surface-2 p-1 rounded-lg border border-border-subtle gap-1">
              {(["pitch", "post", "ask"] as const).map((d) => (
                <button
                  key={d}
                  onClick={() => onSelectDomain(d)}
                  className={`px-3 py-1 rounded-md text-xs font-mono uppercase font-medium transition-all ${
                    selectedDomain === d
                      ? "bg-brand-500 text-white shadow-sm font-semibold"
                      : "text-text-muted hover:text-white"
                  }`}
                >
                  {d}
                </button>
              ))}
            </div>
          </div>

          <div>
            <label className="block text-xs font-mono uppercase text-text-muted mb-1.5">
              Current Context (optional)
            </label>
            <textarea
              rows={2}
              value={context}
              onChange={(e) => setContext(e.target.value)}
              placeholder="e.g. pitching an enterprise AI infrastructure fund on outcome memory"
              className="w-full text-xs font-mono rounded-lg bg-surface-2 border border-border-subtle p-3 focus:outline-none focus:border-brand-500 text-white placeholder:text-text-muted transition-colors"
            />
          </div>

          <button
            onClick={handleGetBrief}
            disabled={isGettingBrief}
            className="w-full bg-surface-2 hover:bg-surface-3 border border-border-subtle hover:border-border-muted text-white text-xs font-semibold py-2.5 rounded-lg transition-colors flex items-center justify-center gap-2 disabled:opacity-50"
          >
            <Search className="w-3.5 h-3.5 text-indigo-400" />
            {isGettingBrief ? "Fetching Brief..." : `Get ${selectedDomain.toUpperCase()} Brief`}
          </button>
        </div>

        {/* Right Side: Record Outcome */}
        <div className="space-y-4 border-t md:border-t-0 md:border-l md:border-border-subtle md:pl-8 pt-4 md:pt-0">
          <h3 className="text-sm font-semibold text-white flex items-center gap-2">
            <PlusCircle className="w-4 h-4 text-emerald-400" />
            Outcome Feedback Layer
          </h3>

          <div className="space-y-3">
            <div>
              <label className="block text-xs font-mono uppercase text-text-muted mb-1.5">
                Action Taken
              </label>
              <input
                type="text"
                value={action}
                onChange={(e) => setAction(e.target.value)}
                placeholder="e.g. opened with problem: stateless agents forget"
                className="w-full text-xs font-mono rounded-lg bg-surface-2 border border-border-subtle px-3 py-2 focus:outline-none focus:border-brand-500 text-white placeholder:text-text-muted transition-colors"
              />
            </div>

            <div>
              <label className="block text-xs font-mono uppercase text-text-muted mb-1.5">
                Observed Outcome
              </label>
              <input
                type="text"
                value={outcome}
                onChange={(e) => setOutcome(e.target.value)}
                placeholder="e.g. got meeting booked same day"
                className="w-full text-xs font-mono rounded-lg bg-surface-2 border border-border-subtle px-3 py-2 focus:outline-none focus:border-brand-500 text-white placeholder:text-text-muted transition-colors"
              />
            </div>

            {/* Signal Selector */}
            <div>
              <label className="block text-xs font-mono uppercase text-text-muted mb-1.5">
                Signal Valuation
              </label>
              <div className="grid grid-cols-3 gap-2">
                <button
                  type="button"
                  onClick={() => setSignal(-1)}
                  className={`py-1.5 px-3 rounded-lg text-xs font-mono font-semibold border transition-all ${
                    signal === -1
                      ? "bg-rose-500/20 border-rose-500 text-rose-300 ring-1 ring-rose-500 shadow-glow-loss"
                      : "bg-surface-2 border-border-subtle text-rose-400/80 hover:bg-rose-500/10"
                  }`}
                >
                  − 1 (Loss)
                </button>
                <button
                  type="button"
                  onClick={() => setSignal(0)}
                  className={`py-1.5 px-3 rounded-lg text-xs font-mono font-semibold border transition-all ${
                    signal === 0
                      ? "bg-surface-3 border-border-muted text-white ring-1 ring-border-muted"
                      : "bg-surface-2 border-border-subtle text-text-muted hover:bg-surface-3"
                  }`}
                >
                  0 (Neutral)
                </button>
                <button
                  type="button"
                  onClick={() => setSignal(1)}
                  className={`py-1.5 px-3 rounded-lg text-xs font-mono font-semibold border transition-all ${
                    signal === 1
                      ? "bg-emerald-500/20 border-emerald-500 text-emerald-300 ring-1 ring-emerald-500 shadow-glow-win"
                      : "bg-surface-2 border-border-subtle text-emerald-400/80 hover:bg-emerald-500/10"
                  }`}
                >
                  + 1 (Win)
                </button>
              </div>
            </div>

            {validationError && (
              <p className="text-xs text-rose-400 font-mono">{validationError}</p>
            )}

            <div className="flex items-center gap-3 pt-1">
              <button
                type="button"
                onClick={handleRecord}
                disabled={isRecording}
                className="flex-1 bg-brand-500 hover:bg-brand-600 text-white text-xs font-semibold py-2.5 px-4 rounded-lg transition-all shadow-glow flex items-center justify-center gap-2 disabled:opacity-50"
              >
                <Send className="w-3.5 h-3.5" />
                {isRecording ? "Writing to Journal..." : "Record Outcome"}
              </button>

              {recordedSuccess && (
                <span className="text-xs font-mono font-semibold text-emerald-300 bg-emerald-500/20 border border-emerald-500/40 px-3 py-2 rounded-lg flex items-center gap-1.5 animate-pulse">
                  <Check className="w-3.5 h-3.5" />
                  Recorded
                </span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
