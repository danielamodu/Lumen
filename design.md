# Lumen Design & Product Specification (2026 Edition)

## Product Identity
- **What is this?**: Lumen is an autonomous outcome memory layer for AI agents. It captures raw action-outcome tuples, synthesizes them into hot/warm/cold memory tiers, and injects actionable briefs into future agent turns so agents get smarter over time without prompt engineering.
- **What should it FEEL like?**: High-performance systems infrastructure — dark obsidian canvas, precision typography, crisp borders, tactile micro-interactions, institutional authority, and zero AI slop.
- **Target Audience**: AI systems engineers, autonomous agent architects, enterprise infrastructure developers.
- **Emotional Hook**: The visceral realization that an agent with outcome memory compounds competence with every single turn.

## Visual Language & Token System
- **Aesthetic**: Minimalist Dark High-Tech Institutional Console & Marketing Layer.
- **Color Palette**:
  - `canvas`: `#080b10` (deepest rich space)
  - `surface-1`: `#0f141c` (base card background)
  - `surface-2`: `#161d28` (elevated panels & inputs)
  - `surface-3`: `#1e2736` (hover & active pill states)
  - `border-subtle`: `#1f2937` / `#253043` (clean hairline dividers)
  - `border-focus`: `#6366f1` (indigo highlight)
  - `text-primary`: `#f9fafb` (pure crisp white)
  - `text-secondary`: `#94a3b8` (clean slate)
  - `text-muted`: `#64748b` (subtle labels)
  - `signal-win`: `#10b981` (emerald-500)
  - `signal-loss`: `#f43f5e` (rose-500)
  - `signal-cross`: `#f59e0b` (amber-500)
  - `brand-accent`: `#6366f1` (indigo-500)
- **Typography**:
  - Sans: Inter / Plus Jakarta Sans for UI copy and headlines.
  - Mono: JetBrains Mono / ui-monospace for code tokens, JSON payloads, memory tier tags, and statistical deltas.
- **Motion Grammar**:
  - Page Transitions: 200ms ease-out.
  - Interactive Tabs & Cards: 150ms hover lift with self-tinted hairline illumination.
  - Value Deltas: 350ms flash animation on outcome recalculation.
  - Fallback: All content rendered statically by default; zero blank hidden content traps.

## Information Architecture & Routing
1. `/` — High-Impact Marketing Landing Page
   - Navigation Header (Logo, Architecture, SDK, Docs, Launch Console)
   - Hero Section: Problem Statement + Live Memory Interactive Simulator
   - 3-Tier Architecture Visualization (HOT / WARM / COLD)
   - Cross-Domain Learning Showcase
   - Interactive SDK Code Walkthrough with Copy Actions
   - The Delete Test (Why Memory is Load-Bearing)
   - Pre-Footer CTA & Technical Footer
2. `/app` — Live Lumen Console (The Full Interactive Application)
   - Live Memory Status Beacon
   - Section 1: 3-Domain Active Intelligence Cards (Pitch, Post, Ask)
   - Section 2: Real-time Outcome Recorder
   - Section 3: 5-Step Automated Demo Runner with Timeline & Logs
   - Section 4: Danger Zone Total Wipe Panel
3. `/docs` — Comprehensive Technical Documentation
   - Quickstart & Installation
   - Memory Tier Specification (Cold Journal, Warm Entities, Hot Cache)
   - Python Core API Reference (`record()`, `brief()`, `get_client()`)
   - Agent Framework Integration (Antigravity, LangChain, CrewAI)
   - REST API Specifications
   - FAQ & Performance Benchmarks
4. `/privacy` — Privacy & Data Sovereignty Policy
   - Local-first storage guarantees
   - Zero telemetry compliance
   - Total Wipe test privacy assurances
5. `/terms` — Terms of Service & Software License
   - MIT Open Source terms
   - Autonomous agent execution liability disclaimers

## Constraints & Anti-Slop Audit
- [x] Zero generic blue-purple gradient blobs
- [x] Content visible without relying on flaky JS entrance animations
- [x] Real code and data models, zero lorem ipsum
- [x] Exact alignment across parallel columns and cards
- [x] Responsive from 320px mobile to ultra-wide
