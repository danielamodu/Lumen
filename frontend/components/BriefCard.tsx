"use client";

import React, { useEffect, useState, useRef } from "react";
import { AlertTriangle, CheckCircle2, GitFork, RotateCw } from "lucide-react";

export interface BriefData {
  warning: string | null;
  pattern: string | null;
  cross_domain: string | null;
  confidence: string;
  raw_outcomes: number;
}

interface BriefCardProps {
  domain: "pitch" | "post" | "ask";
  data: BriefData | null;
  loading: boolean;
  onRefresh: () => void;
}

export const BriefCard: React.FC<BriefCardProps> = ({
  domain,
  data,
  loading,
  onRefresh,
}) => {
  const [flash, setFlash] = useState(false);
  const prevDataRef = useRef<string>("");

  useEffect(() => {
    const currentStr = JSON.stringify(data);
    if (prevDataRef.current && prevDataRef.current !== currentStr) {
      setFlash(true);
      const timer = setTimeout(() => setFlash(false), 400);
      return () => clearTimeout(timer);
    }
    prevDataRef.current = currentStr;
  }, [data]);

  const domainTitle = domain.toUpperCase();
  const outcomesCount = data?.raw_outcomes ?? 0;
  const confidenceText =
    data?.confidence || "0 outcomes recorded. No pattern yet.";

  return (
    <div
      className={`bg-surface-1 rounded-xl border border-border-subtle p-5 shadow-card transition-all duration-200 flex flex-col justify-between ${
        flash ? "animate-flash ring-1 ring-brand-500" : "hover:border-border-muted"
      }`}
    >
      <div>
        {/* Card Top Row */}
        <div className="flex items-center justify-between pb-3 border-b border-border-subtle mb-3">
          <div className="flex items-center gap-2">
            <span className="text-xs font-bold uppercase tracking-wider text-white font-mono">
              {domainTitle}
            </span>
            <span className="bg-surface-2 text-text-secondary text-[11px] px-2 py-0.5 rounded-full font-mono border border-border-subtle">
              {outcomesCount} outcomes
            </span>
          </div>
          <button
            onClick={onRefresh}
            disabled={loading}
            className="text-xs text-indigo-400 hover:text-indigo-300 font-medium transition-colors flex items-center gap-1 disabled:opacity-50"
          >
            <RotateCw className={`w-3 h-3 ${loading ? "animate-spin" : ""}`} />
            <span>Refresh</span>
          </button>
        </div>

        {/* Confidence Tier */}
        <p className="text-xs text-text-muted mb-4 font-mono">
          {confidenceText}
        </p>

        {/* Three Intelligence Rows */}
        <div className="space-y-3">
          {/* Warning */}
          <div className="p-3 rounded-lg bg-rose-500/10 border border-rose-500/20">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-rose-400 mb-1 font-mono">
              <AlertTriangle className="w-3 h-3" />
              Warning
            </div>
            <div className="text-xs font-medium text-rose-300 leading-relaxed">
              {data?.warning ? data.warning : <span className="text-text-muted font-normal font-mono">—</span>}
            </div>
          </div>

          {/* Pattern */}
          <div className="p-3 rounded-lg bg-emerald-500/10 border border-emerald-500/20">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-emerald-400 mb-1 font-mono">
              <CheckCircle2 className="w-3 h-3" />
              Pattern
            </div>
            <div className="text-xs font-medium text-emerald-300 leading-relaxed">
              {data?.pattern ? data.pattern : <span className="text-text-muted font-normal font-mono">—</span>}
            </div>
          </div>

          {/* Cross Domain */}
          <div className="p-3 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <div className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-wider text-amber-400 mb-1 font-mono">
              <GitFork className="w-3 h-3" />
              Cross-Domain
            </div>
            <div className="text-xs font-medium text-amber-300 leading-relaxed">
              {data?.cross_domain ? (
                data.cross_domain
              ) : (
                <span className="text-text-muted font-normal font-mono">—</span>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
