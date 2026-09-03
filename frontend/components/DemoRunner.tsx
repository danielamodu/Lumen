"use client";

import React, { useState } from "react";
import { Play, RotateCcw, Activity } from "lucide-react";
import { BriefData } from "./BriefCard";

interface DemoRunnerProps {
  currentStep: number;
  stepLabel: string;
  actionTaken: string;
  onRunStep: (step: number) => Promise<BriefData | null>;
  onReset: () => Promise<BriefData | null>;
}

export const DemoRunner: React.FC<DemoRunnerProps> = ({
  currentStep,
  stepLabel,
  actionTaken,
  onRunStep,
  onReset,
}) => {
  const [isRunning, setIsRunning] = useState(false);

  const handleNextStep = async () => {
    if (isRunning) return;
    setIsRunning(true);
    const nextStep = currentStep >= 4 ? 1 : currentStep + 1;
    try {
      await onRunStep(nextStep);
      // 2 second delay between steps
      await new Promise((resolve) => setTimeout(resolve, 2000));
    } finally {
      setIsRunning(false);
    }
  };

  const handleReset = async () => {
    if (isRunning) return;
    setIsRunning(true);
    try {
      await onReset();
    } finally {
      setIsRunning(false);
    }
  };

  const progressPercent = (currentStep / 5) * 100;

  return (
    <div className="bg-surface-1 rounded-xl border border-border-subtle p-6 shadow-card text-center">
      <div className="inline-flex items-center gap-2 bg-surface-2 border border-border-muted px-3 py-1 rounded-full text-xs font-mono text-indigo-300 mb-3">
        <Activity className="w-3.5 h-3.5 text-indigo-400" />
        Interactive Learning Loop
      </div>
      <h2 className="text-lg font-bold text-white tracking-tight">Watch Lumen Learn</h2>
      <p className="text-xs text-text-secondary mt-1 mb-5">
        Run the automated 5-step loop sequence to witness real-time pattern shifts
      </p>

      {/* Progress Bar */}
      <div className="max-w-md mx-auto mb-5">
        <div className="flex justify-between text-xs text-text-muted font-mono mb-1.5">
          <span>STEP {currentStep} OF 5</span>
          <span>{Math.round(progressPercent)}%</span>
        </div>
        <div className="w-full bg-surface-2 border border-border-subtle rounded-full h-2 overflow-hidden">
          <div
            className="bg-brand-500 h-2 rounded-full transition-all duration-300 ease-out shadow-glow"
            style={{ width: `${progressPercent}%` }}
          />
        </div>
      </div>

      {/* Step Info Terminal Box */}
      <div className="max-w-lg mx-auto bg-surface-2 border border-border-subtle rounded-lg p-4 mb-6 text-left">
        <div className="text-xs font-semibold text-white mb-1.5 flex items-center justify-between">
          <span>{stepLabel || "Ready to execute demonstration sequence."}</span>
          <span className="text-[10px] font-mono text-text-muted">STATE DELTA</span>
        </div>
        <div className="text-[11px] font-mono text-indigo-300/90 break-words bg-canvas/60 p-2 rounded border border-border-subtle">
          $ {actionTaken || "Click 'Run Next Step' to trigger Step 1 seed"}
        </div>
      </div>

      {/* Controls */}
      <div className="flex items-center justify-center gap-3">
        <button
          onClick={handleNextStep}
          disabled={isRunning}
          className="bg-brand-500 hover:bg-brand-600 text-white text-xs font-semibold py-2.5 px-5 rounded-lg transition-all shadow-glow flex items-center gap-2 disabled:opacity-50"
        >
          {isRunning ? (
            <>
              <svg
                className="animate-spin h-3.5 w-3.5 text-white"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
              >
                <circle
                  className="opacity-25"
                  cx="12"
                  cy="12"
                  r="10"
                  stroke="currentColor"
                  strokeWidth="4"
                ></circle>
                <path
                  className="opacity-75"
                  fill="currentColor"
                  d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                ></path>
              </svg>
              <span>Executing Step...</span>
            </>
          ) : (
            <>
              <Play className="w-3.5 h-3.5 fill-current" />
              <span>▶ Run Next Step</span>
            </>
          )}
        </button>

        <button
          onClick={handleReset}
          disabled={isRunning}
          className="bg-surface-2 hover:bg-surface-3 border border-border-subtle text-text-secondary hover:text-white text-xs font-medium py-2.5 px-4 rounded-lg transition-colors flex items-center gap-1.5 disabled:opacity-50"
        >
          <RotateCcw className="w-3.5 h-3.5" />
          <span>↺ Reset Demo</span>
        </button>
      </div>
    </div>
  );
};
