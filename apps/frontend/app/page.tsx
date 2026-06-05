"use client";

import React, { useState } from "react";

export default function Home() {
  const [copied, setCopied] = useState(false);

  const handleCopyCode = () => {
    navigator.clipboard.writeText(
      `<script src="https://dc-success-coach.vercel.app/widget-loader.js" data-theme="dark" async></script>`
    );
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="min-h-screen bg-[#030712] font-sans text-zinc-100 overflow-x-hidden selection:bg-violet-500/30 selection:text-violet-200">
      {/* Background Glow Orbs */}
      <div className="absolute top-0 left-1/4 -translate-y-1/2 w-[500px] h-[500px] rounded-full bg-violet-600/10 blur-[120px] pointer-events-none" />
      <div className="absolute top-1/3 right-10 w-[400px] h-[400px] rounded-full bg-blue-600/10 blur-[120px] pointer-events-none" />

      {/* Navigation */}
      <header className="sticky top-0 z-50 border-b border-zinc-800/60 bg-[#030712]/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-7xl h-16 items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-gradient-to-br from-violet-600 to-blue-500 shadow-md shadow-violet-500/20">
              <svg className="h-5 w-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <div>
              <span className="font-display text-lg font-bold tracking-tight bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
                AI Success Coach
              </span>
              <span className="ml-2 rounded-full bg-violet-500/10 px-2 py-0.5 text-[10px] font-medium text-violet-400 border border-violet-500/20">
                AI Club Portal
              </span>
            </div>
          </div>
          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-zinc-400">
            <a href="#hero" className="hover:text-white transition-colors">Home</a>
            <a href="#features" className="hover:text-white transition-colors">Features</a>
            <a href="#integration" className="hover:text-white transition-colors">Integration</a>
            <a href="#admin" className="hover:text-white transition-colors">Analytics</a>
          </nav>
          <div className="flex items-center gap-4">
            <a
              href="#chat"
              className="relative inline-flex h-9 items-center justify-center rounded-full bg-gradient-to-r from-violet-600 to-blue-500 px-4 text-xs font-semibold text-white shadow-md shadow-violet-500/20 hover:brightness-110 active:scale-95 transition-all"
            >
              Open Workspace
            </a>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section id="hero" className="relative mx-auto max-w-7xl px-6 pt-16 pb-24 md:pt-24 lg:flex lg:items-center lg:gap-12">
        <div className="flex-1 text-center lg:text-left space-y-6 max-w-2xl mx-auto lg:mx-0">
          <div className="inline-flex items-center gap-2 rounded-full bg-zinc-900 px-3 py-1 text-xs font-medium text-zinc-400 border border-zinc-800/80">
            <span className="flex h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>OpenRouter & Gemini 2.5 Flash Backend Running</span>
          </div>
          <h1 className="font-display text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-white leading-[1.1]">
            Navigate Your College Journey with{" "}
            <span className="bg-gradient-to-r from-violet-400 via-fuchsia-400 to-blue-400 bg-clip-text text-transparent">
              Confidence
            </span>
          </h1>
          <p className="text-zinc-400 text-lg leading-relaxed max-w-lg mx-auto lg:mx-0">
            Evaluate degree course plans, verify financial aid prerequisites, and contact advisors with Dallas College's dedicated, student-built AI assistant.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center lg:justify-start gap-4 pt-2">
            <a
              href="#chat"
              className="flex h-11 w-full sm:w-auto items-center justify-center rounded-full bg-gradient-to-r from-violet-600 to-blue-500 px-6 text-sm font-semibold text-white shadow-lg shadow-violet-600/25 hover:brightness-110 transition-all active:scale-95"
            >
              Start Chatting Now
            </a>
            <a
              href="#integration"
              className="flex h-11 w-full sm:w-auto items-center justify-center rounded-full border border-zinc-800 bg-zinc-900/60 backdrop-blur-sm px-6 text-sm font-semibold text-zinc-300 hover:bg-zinc-800/50 hover:text-white transition-all"
            >
              Get Integration Script
            </a>
          </div>
          {/* Quick FAQ Chips */}
          <div className="pt-6 space-y-3">
            <p className="text-xs font-semibold text-zinc-500 uppercase tracking-wider">Try asking about:</p>
            <div className="flex flex-wrap justify-center lg:justify-start gap-2 max-w-xl mx-auto lg:mx-0">
              {["Cybersecurity degree requirements 🛡️", "FAFSA deadlines 💰", "Richland advisor directory 📞", "Prerequisites for COSC 1436 💻"].map((chip, idx) => (
                <button
                  key={idx}
                  className="rounded-full bg-zinc-900/80 border border-zinc-800 hover:border-zinc-700 px-3.5 py-1.5 text-xs text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800/60 transition-all cursor-pointer"
                >
                  {chip}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Hero Interactive Widget Preview */}
        <div className="flex-1 mt-16 lg:mt-0 max-w-md mx-auto w-full">
          <div className="rounded-2xl border border-zinc-800 bg-[#0b0f19]/80 backdrop-blur-xl shadow-2xl overflow-hidden">
            {/* Widget Header */}
            <div className="flex items-center justify-between border-b border-zinc-850 px-4 py-3 bg-[#0f1524]">
              <div className="flex items-center gap-2">
                <div className="relative flex h-8 w-8 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700">
                  {/* Miniature Mascot SVG */}
                  <svg viewBox="0 0 100 100" className="h-6 w-6">
                    <circle cx="50" cy="50" r="42" fill="#f4f4f5" />
                    <circle cx="38" cy="45" r="4" fill="#030712" />
                    <circle cx="62" cy="45" r="4" fill="#030712" />
                    <rect x="44" y="60" width="12" height="6" rx="3" fill="#ef4444" />
                  </svg>
                  <span className="absolute bottom-0 right-0 h-2 w-2 rounded-full bg-emerald-500 border border-[#0b0f19]" />
                </div>
                <div>
                  <h3 className="text-xs font-bold text-white">AI Success Coach</h3>
                  <p className="text-[10px] text-zinc-500">Always online</p>
                </div>
              </div>
              <div className="flex gap-2">
                <div className="h-2 w-2 rounded-full bg-zinc-700" />
                <div className="h-2 w-2 rounded-full bg-zinc-700" />
              </div>
            </div>

            {/* Chat Area */}
            <div className="p-4 h-[300px] overflow-y-auto space-y-4 text-xs scrollbar-thin">
              {/* User Message */}
              <div className="flex justify-end">
                <div className="rounded-2xl rounded-tr-none bg-violet-600 px-3.5 py-2 text-white max-w-[85%]">
                  What do I need to graduate with an AAS in Cybersecurity?
                </div>
              </div>

              {/* Bot Message */}
              <div className="flex gap-2.5">
                <div className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-zinc-800 border border-zinc-700">
                  <svg viewBox="0 0 100 100" className="h-4 w-4">
                    <circle cx="50" cy="50" r="42" fill="#f4f4f5" />
                  </svg>
                </div>
                <div className="space-y-2 max-w-[85%]">
                  <div className="rounded-2xl rounded-tl-none bg-[#161f33] px-3.5 py-2 text-zinc-300 leading-relaxed border border-zinc-800/80">
                    To graduate with an <span className="text-violet-400 font-semibold">AAS in Cybersecurity</span>, you must complete 60 credit hours, including:
                    <ul className="list-disc pl-4 pt-1 space-y-1">
                      <li>COSC-1436: Programming Fund. I <span className="text-blue-400 font-mono text-[10px] cursor-pointer hover:underline">[1]</span></li>
                      <li>ITSY-1300: Intro to Security <span className="text-blue-400 font-mono text-[10px] cursor-pointer hover:underline">[2]</span></li>
                    </ul>
                  </div>

                  {/* Dynamic Citations Panel */}
                  <div className="rounded-lg bg-[#0e1424] border border-zinc-800/50 p-2 text-[10px] space-y-1">
                    <p className="font-semibold text-zinc-500 uppercase tracking-wider text-[8px]">Sources Used:</p>
                    <div className="flex items-center gap-1.5 text-zinc-400">
                      <span className="font-mono text-violet-400">[1]</span>
                      <a href="#" className="hover:underline truncate">Dallas Catalog: COSC-1436 details 🔗</a>
                    </div>
                    <div className="flex items-center gap-1.5 text-zinc-400">
                      <span className="font-mono text-violet-400">[2]</span>
                      <a href="#" className="hover:underline truncate">Degree Map: Cybersecurity track 🔗</a>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Input Bar */}
            <div className="border-t border-zinc-850 p-3 bg-[#0d1220] flex items-center gap-2">
              <input
                type="text"
                placeholder="Ask about catalogs, pre-requisites..."
                className="flex-1 rounded-full bg-zinc-950 border border-zinc-800 px-3.5 py-1.5 text-xs text-zinc-300 placeholder-zinc-600 focus:outline-none focus:border-violet-500"
                readOnly
              />
              <button className="flex h-7 w-7 items-center justify-center rounded-full bg-violet-600 text-white shrink-0 hover:bg-violet-500">
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="border-t border-zinc-900 bg-[#050814] py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center space-y-3 pb-16">
            <h2 className="font-display text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Architecture Built For Speed and Precision
            </h2>
            <p className="text-zinc-400 max-w-xl mx-auto text-sm">
              We leverage free tiers and advanced RAG practices to power our assistant without any hosting costs.
            </p>
          </div>

          <div className="grid gap-8 sm:grid-cols-2 lg:grid-cols-3">
            {/* Feature 1 */}
            <div className="rounded-2xl border border-zinc-800 bg-[#0a0d1a] p-6 hover:border-zinc-700 transition-colors group">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-violet-600/10 text-violet-400 mb-4 border border-violet-500/20 group-hover:bg-violet-600 group-hover:text-white transition-all">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Semantic RAG Pipeline</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Uses recursive Markdown-aware text chunking and density-optimized vector searches against pgvector to locate answers.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="rounded-2xl border border-zinc-800 bg-[#0a0d1a] p-6 hover:border-zinc-700 transition-colors group">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600/10 text-blue-400 mb-4 border border-blue-500/20 group-hover:bg-blue-600 group-hover:text-white transition-all">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Tool-Calling Engine</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Connects to a mock Ellucian Colleague API, allowing students to check transcripts and financial aid status dynamically.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="rounded-2xl border border-zinc-800 bg-[#0a0d1a] p-6 hover:border-zinc-700 transition-colors group">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-fuchsia-600/10 text-fuchsia-400 mb-4 border border-fuchsia-500/20 group-hover:bg-fuchsia-600 group-hover:text-white transition-all">
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M4 5a1 1 0 01.707-.293l12 12a1 1 0 01-1.414 1.414l-12-12A1 1 0 014 5z" />
                  <path strokeLinecap="round" strokeLinejoin="round" d="M18 4a1 1 0 011 1v12a1 1 0 01-2 0V6.414l-12 12a1 1 0 01-1.414-1.414L15.586 4H18z" />
                </svg>
              </div>
              <h3 className="text-lg font-bold text-white mb-2">Embeddable IFrame Widget</h3>
              <p className="text-zinc-400 text-sm leading-relaxed">
                Isolated iframe widget that slides in and waves to visitors on any campus sub-page without breaking parent layout styles.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* IT Integration Section */}
      <section id="integration" className="mx-auto max-w-7xl px-6 py-24">
        <div className="rounded-2xl border border-zinc-800 bg-gradient-to-b from-[#0a0d1a] to-[#040612] p-8 md:p-12 lg:flex lg:items-center lg:gap-12">
          <div className="flex-1 space-y-6">
            <h2 className="font-display text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Webmaster Integration
            </h2>
            <p className="text-zinc-400 text-sm leading-relaxed max-w-lg">
              University IT departments can mount the chatbot on any official sub-page. The widget automatically binds, displays a floating mascot trigger, and maps dialog constraints correctly.
            </p>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-xs text-zinc-400">
                <svg className="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span>Fully isolated widget iframe CSS sandbox</span>
              </div>
              <div className="flex items-center gap-2 text-xs text-zinc-400">
                <svg className="h-4 w-4 text-violet-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 13l4 4L19 7" />
                </svg>
                <span>Zero configuration initialization script</span>
              </div>
            </div>
          </div>

          <div className="flex-1 mt-8 lg:mt-0 max-w-md w-full">
            <div className="rounded-xl border border-zinc-800 bg-[#05070f] overflow-hidden">
              <div className="flex items-center justify-between border-b border-zinc-850 px-4 py-2 bg-[#090b14]">
                <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-wider">widget-loader.html</span>
                <button
                  onClick={handleCopyCode}
                  className="flex items-center gap-1.5 text-xs text-zinc-400 hover:text-white transition-colors cursor-pointer"
                >
                  <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                  <span>{copied ? "Copied!" : "Copy"}</span>
                </button>
              </div>
              <pre className="p-4 text-xs font-mono text-zinc-400 overflow-x-auto select-all bg-[#03040a]">
                <code>
                  {`<!-- Add to the bottom of the body tag -->
<script 
  src="https://dc-success-coach.vercel.app/widget-loader.js" 
  data-theme="dark" 
  async>
</script>`}
                </code>
              </pre>
            </div>
          </div>
        </div>
      </section>

      {/* Admin Analytics Mock Section */}
      <section id="admin" className="border-t border-zinc-900 bg-[#050814] py-24">
        <div className="mx-auto max-w-7xl px-6">
          <div className="text-center space-y-3 pb-16">
            <h2 className="font-display text-3xl font-extrabold tracking-tight text-white sm:text-4xl">
              Real-time Ingestion & Usage Analytics
            </h2>
            <p className="text-zinc-400 max-w-xl mx-auto text-sm">
              AI Club administrators use the central dashboard to track token rates, RAG citation health, and similarity matching.
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-3 pb-12">
            <div className="rounded-xl border border-zinc-800 bg-[#0a0d1a] p-5">
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Total Conversations</p>
              <p className="text-3xl font-extrabold text-white pt-1">14,821</p>
              <span className="text-[10px] text-emerald-400 flex items-center gap-1 pt-1.5">
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M5 10l7-7m0 0l7 7m-7-7v18" />
                </svg>
                +12% vs last week
              </span>
            </div>
            <div className="rounded-xl border border-zinc-800 bg-[#0a0d1a] p-5">
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Average RAG Latency</p>
              <p className="text-3xl font-extrabold text-white pt-1">920 ms</p>
              <span className="text-[10px] text-emerald-400 flex items-center gap-1 pt-1.5">
                <svg className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M19 13l-7 7m0 0l-7-7m7 7V3" />
                </svg>
                -80ms improvement
              </span>
            </div>
            <div className="rounded-xl border border-zinc-800 bg-[#0a0d1a] p-5">
              <p className="text-xs font-bold text-zinc-500 uppercase tracking-wider">Citation Trust Match</p>
              <p className="text-3xl font-extrabold text-white pt-1">98.4%</p>
              <span className="text-[10px] text-violet-400 flex items-center gap-1 pt-1.5">
                98.4% verified RAG references
              </span>
            </div>
          </div>

          {/* Node Graph Mock (n8n-style) */}
          <div className="rounded-2xl border border-zinc-800 bg-[#080b14]/50 p-6 md:p-8">
            <h4 className="text-xs font-bold text-zinc-500 uppercase tracking-wider mb-6">Inference Node Dataflow (RAG Route)</h4>
            <div className="flex flex-col md:flex-row items-center justify-between gap-6 md:gap-4 relative">
              {/* Node 1 */}
              <div className="rounded-xl border border-zinc-800 bg-[#0e1324] px-4 py-3 text-center w-full max-w-[200px] shadow-lg relative z-10">
                <div className="text-[10px] font-bold text-zinc-500 uppercase">Input Node</div>
                <div className="text-xs font-bold text-white pt-0.5">Student Question</div>
                <div className="text-[9px] text-zinc-500 pt-1">Web UI trigger</div>
              </div>

              {/* Arrow */}
              <div className="h-6 w-0.5 md:h-0.5 md:w-full bg-zinc-800 shrink relative flex items-center justify-center">
                <span className="hidden md:inline h-1.5 w-1.5 rounded-full bg-violet-500 animate-ping" />
              </div>

              {/* Node 2 */}
              <div className="rounded-xl border border-zinc-800 bg-[#0e1324] px-4 py-3 text-center w-full max-w-[200px] shadow-lg relative z-10">
                <div className="text-[10px] font-bold text-zinc-500 uppercase">Embedding Node</div>
                <div className="text-xs font-bold text-white pt-0.5">Gemini text-004</div>
                <div className="text-[9px] text-emerald-400 pt-1">Cached (0.1ms)</div>
              </div>

              {/* Arrow */}
              <div className="h-6 w-0.5 md:h-0.5 md:w-full bg-zinc-800 shrink relative flex items-center justify-center">
                <span className="hidden md:inline h-1.5 w-1.5 rounded-full bg-violet-500 animate-ping" />
              </div>

              {/* Node 3 */}
              <div className="rounded-xl border border-zinc-800 bg-[#0e1324] px-4 py-3 text-center w-full max-w-[200px] shadow-lg relative z-10">
                <div className="text-[10px] font-bold text-zinc-500 uppercase">Vector Database</div>
                <div className="text-xs font-bold text-white pt-0.5">Supabase pgvector</div>
                <div className="text-[9px] text-zinc-500 pt-1">Cosine match &gt; 0.70</div>
              </div>

              {/* Arrow */}
              <div className="h-6 w-0.5 md:h-0.5 md:w-full bg-zinc-800 shrink relative flex items-center justify-center">
                <span className="hidden md:inline h-1.5 w-1.5 rounded-full bg-violet-500 animate-ping" />
              </div>

              {/* Node 4 */}
              <div className="rounded-xl border border-zinc-800 bg-[#0e1324] px-4 py-3 text-center w-full max-w-[200px] shadow-lg relative z-10">
                <div className="text-[10px] font-bold text-zinc-500 uppercase">Generator Node</div>
                <div className="text-xs font-bold text-white pt-0.5">Gemini 2.5 Flash</div>
                <div className="text-[9px] text-violet-400 pt-1">Streaming active</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-zinc-900 py-12 bg-[#03050a]">
        <div className="mx-auto max-w-7xl px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-zinc-500">
          <div className="flex items-center gap-2">
            <div className="h-5 w-5 rounded-md bg-gradient-to-br from-violet-600 to-blue-500 flex items-center justify-center">
              <svg className="h-3 w-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            <span>Dallas College AI Club. © {new Date().getFullYear()} All rights reserved.</span>
          </div>
          <div className="flex gap-4">
            <span>Powered by OpenRouter</span>
            <span>•</span>
            <span>Hobby Tier Architecture</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
