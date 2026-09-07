"use client";
/* eslint-disable @next/next/no-img-element */

import React, { useEffect, useState } from "react";
import Link from "next/link";

const HERO_CODE = [
  "lumen.record({",
  "  domain: 'pitch',",
  "  action: 'led with problem',",
  "  outcome: 'high engagement',",
  "  signal: 1",
  "});",
  "",
  "const briefing = await lumen.brief('pitch');",
  "// brief() returns learned patterns...",
];

const MARKET_CODE = [
  "POST /market/brief HTTP/1.1",
  "Status: 402 Payment Required",
  "",
  ">> Processing 0.01 USDC...",
  ">> Network: Base mainnet",
  ">> Tx: 0x4f2...33d",
  "",
  ">> Retry Success.",
  ">> Response: { aggregate_win_rate: 0.72, ... }",
];

export default function LandingPage() {
  console.log("--> [SSR] RENDERING LANDING PAGE [/]");
  const [heroText, setHeroText] = useState("");
  const [marketText, setMarketText] = useState("");

  // Typewriter effect for Hero code
  useEffect(() => {
    let textIndex = 0;
    let charIndex = 0;
    let timeoutId: NodeJS.Timeout;
    let isCancelled = false;

    function type() {
      if (isCancelled) return;
      if (textIndex < HERO_CODE.length) {
        const current = HERO_CODE[textIndex];
        if (charIndex < current.length) {
          const prev = HERO_CODE.slice(0, textIndex).join("\n");
          const prefix = textIndex > 0 ? "\n" : "";
          setHeroText(prev + prefix + current.substring(0, charIndex + 1));
          charIndex++;
          timeoutId = setTimeout(type, 30 + Math.random() * 25);
        } else {
          textIndex++;
          charIndex = 0;
          timeoutId = setTimeout(type, 600);
        }
      } else {
        timeoutId = setTimeout(() => {
          textIndex = 0;
          charIndex = 0;
          setHeroText("");
          type();
        }, 6000);
      }
    }

    timeoutId = setTimeout(type, 400);
    return () => {
      isCancelled = true;
      clearTimeout(timeoutId);
    };
  }, []);

  // Typewriter effect for Market code
  useEffect(() => {
    let textIndex = 0;
    let charIndex = 0;
    let timeoutId: NodeJS.Timeout;
    let isCancelled = false;

    function type() {
      if (isCancelled) return;
      if (textIndex < MARKET_CODE.length) {
        const current = MARKET_CODE[textIndex];
        if (charIndex < current.length) {
          const prev = MARKET_CODE.slice(0, textIndex).join("\n");
          const prefix = textIndex > 0 ? "\n" : "";
          setMarketText(prev + prefix + current.substring(0, charIndex + 1));
          charIndex++;
          timeoutId = setTimeout(type, 35 + Math.random() * 25);
        } else {
          textIndex++;
          charIndex = 0;
          timeoutId = setTimeout(type, 650);
        }
      } else {
        timeoutId = setTimeout(() => {
          textIndex = 0;
          charIndex = 0;
          setMarketText("");
          type();
        }, 7000);
      }
    }

    timeoutId = setTimeout(type, 1200);
    return () => {
      isCancelled = true;
      clearTimeout(timeoutId);
    };
  }, []);

  return (
    <div className="relative min-h-screen bg-[#0C0A09] text-[#E7E5E4] selection:bg-lime-400/20 selection:text-lime-300">
      <div className="noise-overlay" />

      {/* Navigation */}
      <nav className="fixed top-4 left-1/2 -translate-x-1/2 w-[calc(100%-2rem)] max-w-7xl z-50 flex items-center justify-between px-4 sm:px-6 py-3 glass-nav rounded-full">
        <Link href="/" id="nav-logo-link" className="flex items-center gap-3 group">
          <span className="w-10 h-10 rounded-full bg-lime-400 text-stone-950 flex items-center justify-center group-hover:rotate-12 transition-transform">
            <iconify-icon icon="lucide:brain-circuit" class="text-2xl" />
          </span>
          <span className="serif-display text-xl italic group-hover:text-lime-400 transition-colors">
            Lumen
          </span>
        </Link>
        <div className="hidden md:flex items-center gap-7">
          <a
            href="#problem"
            id="nav-problem"
            className="text-[11px] uppercase tracking-[.2em] text-white/45 hover:text-white transition-colors"
          >
            Problem
          </a>
          <a
            href="#how-it-works"
            id="nav-how"
            className="text-[11px] uppercase tracking-[.2em] text-white/45 hover:text-white transition-colors"
          >
            How it Works
          </a>
          <a
            href="#market"
            id="nav-market"
            className="text-[11px] uppercase tracking-[.2em] text-white/45 hover:text-white transition-colors"
          >
            Market
          </a>
        </div>
        <Link
          href="/app"
          id="nav-cta"
          className="btn-lime px-5 py-2.5 rounded-full text-[11px] uppercase tracking-[.18em]"
        >
          Launch Console
        </Link>
      </nav>

      <main id="top">
        {/* Hero Section */}
        <section className="hero-glow relative min-h-screen overflow-hidden pt-32 sm:pt-40 pb-20 px-6">
          <div className="absolute inset-0 pointer-events-none opacity-60">
            <svg
              className="w-full h-full"
              viewBox="0 0 1440 900"
              fill="none"
              aria-hidden="true"
            >
              <g className="spin-slow" opacity=".28" transform="translate(1080 360)">
                <circle r="245" stroke="#D4F268" strokeWidth="1" strokeDasharray="2 12" />
                <circle r="178" stroke="#8172E8" strokeWidth="1" />
                <path
                  d="M0-245L178 0 0 245-178 0zM-173-173L173 173M173-173L-173 173"
                  stroke="#D4F268"
                  strokeWidth="1"
                />
              </g>
              <path
                className="pulse-line"
                d="M0 735C245 590 350 790 570 630S930 360 1440 530"
                stroke="#D4F268"
                strokeOpacity=".18"
              />
              <circle className="float-fast" cx="1210" cy="160" r="4" fill="#D4F268" />
              <circle className="float-slow" cx="930" cy="680" r="3" fill="#8172E8" />
            </svg>
          </div>

          <div className="relative max-w-7xl mx-auto grid lg:grid-cols-[.9fr_1.1fr] gap-14 lg:gap-20 items-center">
            <div className="relative z-10">
              <div className="flex items-center gap-3 mb-8">
                <span className="mono-technical text-lime-400">SYSTEM / 001</span>
                <span className="h-px w-16 bg-lime-400/40" />
                <span className="mono-technical text-white/30">OUTCOME MEMORY</span>
              </div>
              <h1 className="hero-title serif-display text-[4.5rem] sm:text-8xl lg:text-[8.2rem] font-extralight leading-[.82] tracking-[-.06em]">
                Your agents
                <br />
                forget.
                <br />
                <span className="italic text-lime-300">Lumen</span>
                <br />
                <span className="text-white/75">remembers.</span>
              </h1>
              <p className="mt-9 max-w-lg text-white/55 text-lg sm:text-xl leading-relaxed">
                The outcome memory layer that makes any agent learn from experience. Not fine-tuning. Not RAG. Just memory.
              </p>
              <div className="flex flex-wrap gap-4 mt-9">
                <Link
                  href="/app"
                  id="hero-demo-btn"
                  className="btn-lime px-7 py-4 rounded-full text-xs uppercase tracking-[.18em] inline-flex items-center gap-3"
                >
                  Watch the Demo <iconify-icon icon="lucide:arrow-up-right" />
                </Link>
                <a
                  href="https://github.com/danielamodu/Lumen"
                  target="_blank"
                  rel="noopener noreferrer"
                  id="hero-gh-btn"
                  className="px-7 py-4 rounded-full border border-white/20 text-xs uppercase tracking-[.18em] hover:border-lime-400/60 hover:text-lime-300 transition-colors inline-flex items-center gap-3"
                >
                  View on GitHub <iconify-icon icon="mdi:github" />
                </a>
              </div>
              <div className="float-slow absolute -right-8 sm:-right-20 top-10 sm:top-28 w-44 sm:w-56 p-5 sm:p-6 bg-lime-300 text-stone-950 rounded-[24px] rotate-6 shadow-[0_30px_70px_rgba(0,0,0,.5)] z-20">
                <span className="mono-technical text-stone-950/50">FIELD NOTE / 01</span>
                <h4 className="serif-display text-xl sm:text-2xl font-bold leading-tight mt-3">
                  Persistence is Intelligence.
                </h4>
                <p className="text-[10px] uppercase tracking-widest opacity-60 border-t border-black/10 pt-3 mt-4">
                  Core theory
                </p>
              </div>
            </div>

            <div className="relative min-h-[570px] flex items-center justify-center">
              <div className="absolute w-[90%] h-[90%] rounded-full bg-violet-500/10 blur-3xl" />
              <svg
                className="relative w-full max-w-[650px]"
                viewBox="0 0 700 650"
                fill="none"
                aria-label="Abstract architectural memory structure"
              >
                <defs>
                  <linearGradient id="crystal" x1="0" y1="0" x2="1" y2="1">
                    <stop stopColor="#D4F268" stopOpacity=".9" />
                    <stop offset="1" stopColor="#8172E8" stopOpacity=".1" />
                  </linearGradient>
                  <filter id="glow">
                    <feGaussianBlur stdDeviation="5" result="blur" />
                    <feMerge>
                      <feMergeNode in="blur" />
                      <feMergeNode in="SourceGraphic" />
                    </feMerge>
                  </filter>
                </defs>
                <path
                  d="M70 545L160 110 350 35 550 135 635 545H70Z"
                  fill="url(#crystal)"
                  fillOpacity=".08"
                  stroke="#E7E5E4"
                  strokeOpacity=".28"
                />
                <path
                  d="M105 510L182 145 350 82 515 160 600 510H105Z"
                  stroke="#D4F268"
                  strokeOpacity=".58"
                />
                <path
                  d="M160 510L220 185 350 125 480 190 540 510"
                  stroke="#8172E8"
                  strokeOpacity=".8"
                />
                <path
                  d="M215 510V255L350 166 485 255V510M270 510V300L350 245 430 300V510"
                  stroke="#E7E5E4"
                  strokeOpacity=".55"
                />
                <path
                  d="M275 510V340Q350 270 425 340V510"
                  stroke="#D4F268"
                  strokeWidth="3"
                  filter="url(#glow)"
                />
                <path
                  d="M350 35V166M182 145L350 245 515 160M105 510L350 245 600 510M70 545H635"
                  stroke="#E7E5E4"
                  strokeOpacity=".2"
                />
                <g className="float-fast">
                  <circle cx="350" cy="245" r="9" fill="#D4F268" />
                  <circle cx="350" cy="245" r="22" stroke="#D4F268" strokeOpacity=".3" />
                </g>
                <g className="mono-technical" fill="#E7E5E4" fillOpacity=".65">
                  <text x="84" y="574">COLD</text>
                  <text x="320" y="574">WARM</text>
                  <text x="565" y="574">HOT</text>
                  <text x="520" y="112">MEMORY / 03</text>
                </g>
              </svg>

              <div className="absolute bottom-2 left-1/2 -translate-x-1/2 code-container p-5 w-[92%] max-w-[550px]">
                <div className="flex items-center justify-between mb-4">
                  <span className="mono-technical text-white/30">LIVE MEMORY CHAIN</span>
                  <span className="flex items-center gap-2 text-[10px] uppercase text-lime-300">
                    <i className="w-2 h-2 rounded-full bg-lime-300 animate-pulse" /> Writing
                  </span>
                </div>
                <pre id="hero-code" className="text-lime-300 whitespace-pre-wrap leading-6 text-xs sm:text-sm font-mono min-h-[160px]">
                  {heroText}
                  <span className="cursor" />
                </pre>
              </div>
            </div>
          </div>

          <div className="relative max-w-7xl mx-auto mt-8 flex justify-between mono-technical text-white/25">
            <span>SCROLL TO INSPECT</span>
            <span>LATENCY: 034ms ↓</span>
          </div>
        </section>

        <div className="serrated-divider" />

        {/* Problem Section */}
        <section id="problem" className="relative px-6 py-28 sm:py-36 overflow-hidden line-grid">
          <div className="max-w-7xl mx-auto relative">
            <div className="flex items-center gap-4 mb-6">
              <span className="mono-technical text-lime-400">02 / THE FAILURE LOOP</span>
              <span className="h-px w-24 bg-lime-400/40" />
            </div>
            <h2 className="serif-display text-5xl sm:text-7xl lg:text-8xl font-extralight leading-[.88] max-w-5xl">
              Agents are brilliant
              <br />
              in one session.
              <br />
              <span className="italic text-white/45">Amnesiac</span> the next.
            </h2>
            <div className="relative mt-20 grid md:grid-cols-3 gap-6 items-start">
              <div className="hidden md:block absolute top-1/2 left-[16%] right-[16%] border-t border-dashed border-red-400/40" />

              {/* Session 01 */}
              <div className="card relative p-7 sm:p-9 md:translate-y-8 overflow-hidden group hover:-translate-y-1 transition-transform">
                <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-transparent pointer-events-none" />
                <div className="relative">
                  <div className="flex justify-between items-center mb-12">
                    <span className="mono-technical text-white/35">SESSION / 01</span>
                    <span className="text-red-400 text-xs">SIGNAL LOST</span>
                  </div>
                  <svg viewBox="0 0 180 130" className="w-full h-32 mb-8" fill="none">
                    <circle
                      cx="90"
                      cy="65"
                      r="44"
                      stroke="#EF4444"
                      strokeOpacity=".7"
                      strokeWidth="2"
                      strokeDasharray="8 8"
                    />
                    <circle cx="90" cy="65" r="17" fill="#D4F268" />
                    <path d="M90 10V37M90 93v27M35 65h28M117 65h28" stroke="#E7E5E4" strokeOpacity=".35" />
                    <path d="M126 27l25-18M126 103l25 18" stroke="#EF4444" strokeWidth="3" />
                  </svg>
                  <span className="text-[10px] uppercase tracking-widest text-white/35">Repeated action</span>
                  <p className="text-lg mt-2">
                    Led with product demo → <span className="text-red-400">Ghosted</span>
                  </p>
                </div>
              </div>

              {/* Session 02 */}
              <div className="card relative p-7 sm:p-9 md:-translate-y-5 overflow-hidden group hover:-translate-y-7 transition-transform">
                <div className="absolute inset-0 bg-gradient-to-br from-orange-500/10 to-transparent pointer-events-none" />
                <div className="relative">
                  <div className="flex justify-between items-center mb-12">
                    <span className="mono-technical text-white/35">SESSION / 02</span>
                    <span className="text-orange-400 text-xs">NO RESPONSE</span>
                  </div>
                  <svg viewBox="0 0 180 130" className="w-full h-32 mb-8" fill="none">
                    <circle
                      cx="90"
                      cy="65"
                      r="45"
                      stroke="#F97316"
                      strokeOpacity=".6"
                      strokeWidth="2"
                    />
                    <path
                      d="M48 38l84 54M132 38L48 92"
                      stroke="#F97316"
                      strokeWidth="3"
                      strokeDasharray="5 7"
                    />
                    <circle cx="48" cy="38" r="6" fill="#F97316" />
                    <circle cx="132" cy="92" r="6" fill="#F97316" />
                    <path d="M90 20v90M45 65h90" stroke="#E7E5E4" strokeOpacity=".2" />
                  </svg>
                  <span className="text-[10px] uppercase tracking-widest text-white/35">
                    Disconnected pattern
                  </span>
                  <p className="text-lg mt-2">
                    Led with product demo → <span className="text-orange-400">No response</span>
                  </p>
                </div>
              </div>

              {/* Session 03 */}
              <div className="card relative p-7 sm:p-9 md:translate-y-12 overflow-hidden group hover:translate-y-10 transition-transform">
                <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-transparent pointer-events-none" />
                <div className="relative">
                  <div className="flex justify-between items-center mb-12">
                    <span className="mono-technical text-white/35">SESSION / 03</span>
                    <span className="text-red-400 text-xs">LOOP DETECTED</span>
                  </div>
                  <svg viewBox="0 0 180 130" className="w-full h-32 mb-8" fill="none">
                    <path
                      d="M35 65c0-30 25-50 55-50s55 20 55 50-25 50-55 50-55-20-55-50Z"
                      stroke="#EF4444"
                      strokeWidth="2"
                      strokeDasharray="13 8"
                    />
                    <path d="M90 15v30M90 85v30M35 65h30M115 65h30" stroke="#E7E5E4" strokeOpacity=".25" />
                    <path d="M72 47l36 36M108 47L72 83" stroke="#D4F268" strokeWidth="2" />
                    <circle cx="90" cy="65" r="7" fill="#EF4444" />
                  </svg>
                  <span className="text-[10px] uppercase tracking-widest text-white/35">Memory absent</span>
                  <p className="text-lg mt-2">
                    Led with product demo → <span className="text-red-400">Ghosted again</span>
                  </p>
                </div>
              </div>
            </div>
            <p className="serif-display text-4xl sm:text-5xl text-center italic text-lime-300 mt-32">
              Lumen breaks this loop.
            </p>
          </div>
        </section>

        <div className="serrated-divider" />

        {/* How it works section */}
        <section id="how-it-works" className="relative px-6 py-28 sm:py-40 overflow-hidden bg-[#11100f]">
          <div className="absolute inset-0 opacity-25 line-grid" />
          <div className="relative max-w-7xl mx-auto">
            <div className="text-center mb-16">
              <span className="mono-technical text-lime-400">03 / THE ARCHITECTURE</span>
              <h2 className="serif-display text-6xl sm:text-8xl font-extralight mt-5">
                The memory <span className="italic text-lime-300">loop.</span>
              </h2>
              <p className="text-white/45 max-w-xl mx-auto mt-6">
                A living architecture that turns every outcome into the next advantage.
              </p>
            </div>

            <div className="relative max-w-6xl mx-auto rounded-[40px] border border-white/10 bg-stone-950/60 p-5 sm:p-12 overflow-hidden">
              <svg viewBox="0 0 1000 530" className="w-full" fill="none" aria-label="Three tier memory architecture">
                <defs>
                  <linearGradient id="tierGlow" x1="0" y1="0" x2="1" y2="1">
                    <stop stopColor="#D4F268" stopOpacity=".8" />
                    <stop offset="1" stopColor="#8172E8" stopOpacity=".15" />
                  </linearGradient>
                </defs>
                <path d="M90 455H910M145 455L215 110H785L855 455" stroke="#E7E5E4" strokeOpacity=".17" />
                <path d="M215 110L500 35 785 110 700 455H300L215 110Z" stroke="#8172E8" strokeOpacity=".55" />
                <path d="M270 420L320 170 500 105 680 170 730 420" stroke="#D4F268" strokeOpacity=".55" />
                <path
                  d="M335 420V235L500 145 665 235V420M400 420V280L500 220 600 280V420"
                  stroke="#E7E5E4"
                  strokeOpacity=".48"
                />
                <path d="M430 420V315Q500 245 570 315V420" stroke="#D4F268" strokeWidth="3" />
                <path
                  className="dash-flow"
                  d="M230 405C280 340 290 255 350 205S445 130 500 105"
                  stroke="#D4F268"
                  strokeWidth="2"
                />
                <path
                  className="dash-flow"
                  d="M500 105C555 130 650 160 680 250S715 355 770 405"
                  stroke="#8172E8"
                  strokeWidth="2"
                />
                <g className="float-fast">
                  <circle cx="500" cy="105" r="8" fill="#D4F268" />
                  <circle cx="500" cy="105" r="20" stroke="#D4F268" strokeOpacity=".25" />
                </g>
                <g className="mono-technical" fill="#E7E5E4">
                  <text x="115" y="485">COLD TIER / JOURNAL</text>
                  <text x="410" y="485">WARM TIER / PATTERNS</text>
                  <text x="745" y="485">HOT TIER / BRIEF</text>
                </g>
                <g fill="#D4F268" fillOpacity=".8">
                  <circle cx="230" cy="405" r="4" />
                  <circle cx="350" cy="205" r="4" />
                  <circle cx="770" cy="405" r="4" />
                </g>
              </svg>

              <div className="grid md:grid-cols-3 gap-5 mt-4">
                <div className="rounded-2xl border border-white/10 bg-white/[.03] p-5">
                  <span className="mono-technical text-lime-300">01 / COLD TIER</span>
                  <p className="text-sm text-white/60 mt-3">Outcome written to journal. Append-only. Tamper-evident.</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[.03] p-5">
                  <span className="mono-technical text-lime-300">02 / WARM TIER</span>
                  <p className="text-sm text-white/60 mt-3">Pattern extracted from history. Updated after every outcome.</p>
                </div>
                <div className="rounded-2xl border border-white/10 bg-white/[.03] p-5">
                  <span className="mono-technical text-lime-300">03 / HOT TIER</span>
                  <p className="text-sm text-white/60 mt-3">Brief surfaced before acting. Changes every session.</p>
                </div>
              </div>
            </div>

            <div className="relative max-w-3xl mx-auto mt-16 p-8 sm:p-12 border border-lime-300/30 rounded-[30px] bg-lime-300/[.06] text-center overflow-hidden">
              <div className="absolute -top-20 left-1/2 -translate-x-1/2 w-64 h-40 bg-lime-300/10 blur-3xl" />
              <p className="relative serif-display text-3xl sm:text-4xl italic font-light">
                “Delete Sibyl memory → loop breaks → agent goes blind.”
              </p>
            </div>
          </div>
        </section>

        <div className="serrated-divider" />

        {/* Delete Test Section */}
        <section id="delete-test" className="relative px-6 py-28 sm:py-40 overflow-hidden">
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_40%,rgba(239,68,68,.12),transparent_34%)]" />
          <div className="relative max-w-6xl mx-auto grid lg:grid-cols-[.9fr_1.1fr] gap-16 items-center">
            <div>
              <span className="mono-technical text-red-400">04 / DESTRUCTIVE PROOF</span>
              <h2 className="serif-display text-6xl sm:text-8xl font-extralight leading-[.86] mt-6">
                The <span className="italic text-red-400">load-bearing</span> test.
              </h2>
              <p className="text-white/55 text-lg mt-8 leading-relaxed">
                Delete the Sibyl memory file. brief() returns nothing. Agents have no patterns. Cross-domain learning collapses. The loop is broken. Without Sibyl, Lumen is a logging tool. With it, Lumen learns.
              </p>
              <Link
                href="/app"
                id="test-live-btn"
                className="inline-flex items-center gap-4 mt-9 text-red-300 uppercase tracking-[.2em] text-xs font-bold group"
              >
                See it live{" "}
                <span className="w-12 h-12 rounded-full border border-red-400 flex items-center justify-center group-hover:bg-red-400 group-hover:text-stone-950 transition-all">
                  <iconify-icon icon="lucide:arrow-right" />
                </span>
              </Link>
            </div>
            <div className="relative aspect-square max-w-[560px] mx-auto w-full">
              <svg viewBox="0 0 560 560" className="w-full h-full" fill="none">
                <circle
                  cx="280"
                  cy="280"
                  r="202"
                  stroke="#EF4444"
                  strokeOpacity=".18"
                  strokeDasharray="4 13"
                  className="spin-slow"
                />
                <circle
                  cx="280"
                  cy="280"
                  r="132"
                  stroke="#EF4444"
                  strokeOpacity=".45"
                  strokeDasharray="2 9"
                />
                <path
                  d="M280 56V188M280 372V504M56 280H188M372 280H504"
                  stroke="#EF4444"
                  strokeOpacity=".55"
                  strokeDasharray="9 9"
                  className="dash-flow"
                />
                <path d="M178 178L382 382M382 178L178 382" stroke="#EF4444" strokeWidth="3" />
                <path d="M280 120L440 280 280 440 120 280 280 120Z" stroke="#E7E5E4" strokeOpacity=".3" />
                <path d="M230 230L330 330M330 230L230 330" stroke="#EF4444" strokeWidth="7" />
                <circle cx="280" cy="280" r="28" fill="#EF4444" fillOpacity=".17" stroke="#EF4444" />
                <g fill="#EF4444">
                  <circle cx="120" cy="280" r="6" />
                  <circle cx="440" cy="280" r="6" />
                  <circle cx="280" cy="120" r="6" />
                  <circle cx="280" cy="440" r="6" />
                </g>
              </svg>
              <div className="absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 text-center">
                <iconify-icon icon="lucide:unlink" class="text-4xl text-red-400" />
                <p className="mono-technical text-red-300 mt-3">MEMORY PURGED</p>
              </div>
            </div>
          </div>
        </section>

        <div className="serrated-divider" />

        {/* Market Section */}
        <section id="market" className="relative px-6 py-28 sm:py-36 bg-[#11100f] overflow-hidden">
          <div className="relative max-w-7xl mx-auto grid lg:grid-cols-[.85fr_1.15fr] gap-16 items-center">
            <div>
              <span className="mono-technical text-lime-400">05 / THE MARKET</span>
              <h2 className="serif-display text-6xl sm:text-7xl font-extralight leading-[.9] mt-6">
                Personal memory becomes <span className="italic text-lime-300">collective intelligence.</span>
              </h2>
              <p className="text-white/55 mt-8 max-w-lg leading-relaxed">
                The x402 market endpoint enables autonomous agents to pay 0.01 USDC on Base to query aggregate patterns across all users. Memory is no longer isolated: it is a shared intelligence asset.
              </p>
              <div className="mt-8 inline-flex items-center gap-4 p-4 rounded-2xl border border-white/10 bg-white/[.03]">
                <span className="w-11 h-11 rounded-full bg-blue-500/15 text-blue-400 flex items-center justify-center">
                  <iconify-icon icon="simple-icons:base" class="text-xl" />
                </span>
                <span>
                  <span className="block text-xs uppercase tracking-widest">Settlement Layer</span>
                  <span className="block text-sm text-white/40">Optimistic Rollup on Base</span>
                </span>
              </div>
            </div>

            <div className="relative rounded-[32px] border border-white/10 bg-stone-950 p-6 sm:p-9 min-h-[440px] overflow-hidden">
              <div className="absolute inset-0 opacity-20 line-grid" />
              <svg viewBox="0 0 650 360" className="relative w-full" fill="none">
                <path className="dash-flow" d="M70 180H205M245 180H380M420 180H580" stroke="#D4F268" strokeWidth="2" />
                <circle cx="70" cy="180" r="30" fill="#D4F268" fillOpacity=".12" stroke="#D4F268" />
                <circle cx="225" cy="180" r="30" fill="#8172E8" fillOpacity=".16" stroke="#8172E8" />
                <circle cx="400" cy="180" r="30" fill="#F97316" fillOpacity=".14" stroke="#F97316" />
                <circle cx="580" cy="180" r="30" fill="#D4F268" fillOpacity=".12" stroke="#D4F268" />
                <g className="mono-technical" textAnchor="middle">
                  <text x="70" y="185" fill="#D4F268">AGENT</text>
                  <text x="225" y="185" fill="#E7E5E4">402</text>
                  <text x="400" y="185" fill="#F97316">PAY</text>
                  <text x="580" y="185" fill="#D4F268">DATA</text>
                </g>
                <path
                  d="M225 150V80H400V150M400 210V280H225V210"
                  stroke="#E7E5E4"
                  strokeOpacity=".2"
                  strokeDasharray="4 6"
                />
                <text x="300" y="68" fill="#E7E5E4" fillOpacity=".4" className="mono-technical">
                  PAYMENT REQUIRED
                </text>
                <text x="275" y="310" fill="#D4F268" fillOpacity=".7" className="mono-technical">
                  RETRY / QUERY SUCCESS
                </text>
              </svg>

              <div className="relative code-container p-5 mt-2">
                <div className="flex justify-between mb-3">
                  <span className="mono-technical text-white/30">NETWORK REQUEST // 402</span>
                  <span className="w-2 h-2 rounded-full bg-lime-300 animate-pulse" />
                </div>
                <pre id="market-code" className="text-lime-300 whitespace-pre-wrap leading-6 text-xs sm:text-sm font-mono min-h-[150px]">
                  {marketText}
                  <span className="cursor" />
                </pre>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="relative bg-[#7565D7] text-white overflow-hidden">
        <svg
          className="footer-wave"
          viewBox="0 0 1440 115"
          preserveAspectRatio="none"
          aria-hidden="true"
        >
          <path
            d="M0 74C105 20 185 108 300 56S500 18 620 62s220 40 330-8 230-44 315 8 120 30 175-2V115H0Z"
            fill="#11100f"
          />
          <path
            d="M0 84C105 30 185 118 300 66S500 28 620 72s220 40 330-8 230-44 315 8 120 30 175-2"
            stroke="#D4F268"
            strokeOpacity=".35"
            fill="none"
          />
        </svg>
        <div className="relative max-w-7xl mx-auto px-6 pb-10 pt-4">
          <div className="grid lg:grid-cols-[1.3fr_1fr_1fr_1fr] gap-12 lg:gap-8 items-start">
            <div>
              <div className="flex items-center gap-3">
                <span className="w-12 h-12 rounded-full bg-lime-300 text-stone-950 flex items-center justify-center">
                  <iconify-icon icon="lucide:brain-circuit" class="text-2xl" />
                </span>
                <span className="serif-display text-3xl italic">Lumen</span>
              </div>
              <p className="text-sm text-white/70 max-w-xs mt-6">
                The outcomes memory layer for the agentic era.
              </p>
              <div className="flex gap-3 mt-7">
                <a
                  href="https://github.com/danielamodu/Lumen"
                  target="_blank"
                  rel="noopener noreferrer"
                  id="footer-gh"
                  aria-label="GitHub"
                  className="w-9 h-9 rounded-full border border-white/30 flex items-center justify-center hover:bg-white hover:text-[#7565D7] transition-colors"
                >
                  <iconify-icon icon="mdi:github" />
                </a>
                <a
                  href="https://x.com/szrxbt"
                  target="_blank"
                  rel="noopener noreferrer"
                  id="footer-x"
                  aria-label="X"
                  className="w-9 h-9 rounded-full border border-white/30 flex items-center justify-center hover:bg-white hover:text-[#7565D7] transition-colors"
                >
                  <iconify-icon icon="simple-icons:x" />
                </a>
                <a
                  href="https://www.linkedin.com/in/daniel-amodu-07306b433/"
                  target="_blank"
                  rel="noopener noreferrer"
                  id="footer-linkedin"
                  aria-label="LinkedIn"
                  className="w-9 h-9 rounded-full border border-white/30 flex items-center justify-center hover:bg-white hover:text-[#7565D7] transition-colors"
                >
                  <iconify-icon icon="mdi:linkedin" />
                </a>
              </div>
            </div>

            <div>
              <h3 className="text-[10px] uppercase tracking-[.22em] text-white/55 mb-5">Explore</h3>
              <div className="space-y-3 text-sm">
                <a href="#problem" id="footer-problem" className="block hover:text-lime-300 transition-colors">
                  The problem
                </a>
                <a href="#how-it-works" id="footer-how" className="block hover:text-lime-300 transition-colors">
                  How it works
                </a>
                <a href="#market" id="footer-market" className="block hover:text-lime-300 transition-colors">
                  Memory market
                </a>
              </div>
            </div>

            <div>
              <h3 className="text-[10px] uppercase tracking-[.22em] text-white/55 mb-5">Infrastructure</h3>
              <div className="space-y-3 text-sm text-white/80">
                <p className="flex items-center gap-2">
                  <iconify-icon icon="lucide:shield-check" /> Powered by Sibyl Memory
                </p>
                <p className="flex items-center gap-2">
                  <iconify-icon icon="lucide:link" /> Built on Base
                </p>
                <p className="flex items-center gap-2">
                  <iconify-icon icon="lucide:activity" /> Systems operational
                </p>
              </div>
            </div>

            <div>
              <h3 className="text-[10px] uppercase tracking-[.22em] text-white/55 mb-5">Stay close</h3>
              <p className="text-sm text-white/75 mb-4">Follow the memory layer as it learns.</p>
              <form onSubmit={(e) => e.preventDefault()} className="flex border-b border-white/40 pb-2">
                <label htmlFor="footer-email" className="sr-only">
                  Email address
                </label>
                <input
                  id="footer-email"
                  type="email"
                  placeholder="your@email.com"
                  className="bg-transparent outline-none w-full placeholder:text-white/45 text-sm"
                />
                <button
                  type="submit"
                  id="footer-subscribe"
                  aria-label="Subscribe"
                  className="text-lime-300 hover:text-white transition-colors"
                >
                  <iconify-icon icon="lucide:arrow-up-right" class="text-xl" />
                </button>
              </form>
            </div>
          </div>

          <div className="mt-16 pt-6 border-t border-white/20 flex flex-col sm:flex-row justify-between gap-3 text-[10px] uppercase tracking-[.18em] text-white/55">
            <span>© 2026 Lumen Protocol. All rights reserved.</span>
            <span className="mono-technical">API: lumen-memory-production.up.railway.app</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
