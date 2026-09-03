"use client";

import React, { useState } from "react";
import { Trash2, AlertOctagon } from "lucide-react";

interface WipePanelProps {
  onWipe: () => Promise<void>;
}

export const WipePanel: React.FC<WipePanelProps> = ({ onWipe }) => {
  const [isWiping, setIsWiping] = useState(false);

  const handleWipeClick = async () => {
    const confirmed = window.confirm(
      "Delete all Sibyl memory? This will clear all outcomes and patterns. This cannot be undone."
    );
    if (!confirmed) return;

    setIsWiping(true);
    try {
      await onWipe();
    } finally {
      setIsWiping(false);
    }
  };

  return (
    <div className="bg-rose-950/20 border border-rose-900/30 rounded-xl p-5 shadow-card flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
      <div className="flex items-start gap-3">
        <div className="w-8 h-8 rounded-lg bg-rose-500/10 border border-rose-500/20 flex items-center justify-center text-rose-400 shrink-0">
          <AlertOctagon className="w-4 h-4" />
        </div>
        <div>
          <div className="flex items-center gap-2">
            <span className="text-rose-400 font-semibold text-xs font-mono uppercase tracking-wider">
              Danger Zone · Load-Bearing Delete Test
            </span>
          </div>
          <p className="text-xs text-rose-300/80 mt-0.5 leading-relaxed">
            Permanently delete local Sibyl SQLite memory file. Demonstrates how stateless agents go blind without Lumen.
          </p>
        </div>
      </div>

      <button
        onClick={handleWipeClick}
        disabled={isWiping}
        className="bg-rose-500/10 hover:bg-rose-500/20 text-rose-300 border border-rose-500/30 hover:border-rose-500/50 text-xs font-semibold py-2 px-4 rounded-lg transition-all flex items-center justify-center gap-1.5 shadow-xs disabled:opacity-50 shrink-0 self-start sm:self-auto font-mono"
      >
        <Trash2 className="w-3.5 h-3.5" />
        {isWiping ? "Wiping Memory..." : "Wipe Memory"}
      </button>
    </div>
  );
};
