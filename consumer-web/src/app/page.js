"use client";

import Link from "next/link";
import { ShieldCheck, QrCode, Search, Award, Sprout, ArrowRight } from "lucide-react";
import { MOCK_BATCHES } from "../lib/mockData";

export default function Home() {
  const sampleBatches = Object.values(MOCK_BATCHES);

  return (
    <main className="min-h-screen honey-hero-mesh flex flex-col justify-between">
      
      <header className="w-full max-w-4xl mx-auto px-6 py-6 flex items-center justify-between border-b border-amber-900/10">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 rounded-full verdict-seal-badge flex items-center justify-center text-[#24140D] font-bold text-lg shadow-sm">
            🍯
          </div>
          <div>
            <span className="font-serif text-2xl font-bold tracking-tight text-[#24140D]">
              HoneyChain
            </span>
            <span className="block text-xs font-mono uppercase tracking-widest text-amber-800/80">
              KVIC · MSME Verification
            </span>
          </div>
        </div>

        <div className="flex items-center space-x-2 text-xs font-mono bg-amber-100/60 px-3 py-1.5 rounded-full border border-amber-300/60 text-amber-950">
          <span className="w-2 h-2 rounded-full bg-emerald-600 animate-pulse" />
          <span>Polygon Amoy Live</span>
        </div>
      </header>

      
      <div className="w-full max-w-2xl mx-auto px-6 py-12 flex-1 flex flex-col justify-center">
        
        <div className="text-center mb-10">
          <div className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#EBA818]/20 border border-[#EBA818]/40 text-xs font-medium text-[#6F3E14] mb-4">
            
            <span>🚧 This is a visual preview. The full application is currently under active development.</span>
          </div>
          <h1 className="font-serif text-4xl sm:text-5xl font-bold text-[#24140D] tracking-tight leading-tight">
            Trace Your Honey From Hive to Jar
          </h1>
          <p className="mt-4 text-base sm:text-lg text-amber-950/80 max-w-xl mx-auto leading-relaxed">
            Verify 100% pure rural honey on the blockchain. Inspect lab purity certificates and witness the fair-trade royalty returned directly to the beekeeper.
          </p>
        </div>

        
        <div className="bg-white/85 backdrop-blur-md rounded-2xl p-6 shadow-xl border border-amber-200/70 mb-10">
          <form
            action="/verify"
            method="GET"
            onSubmit={(e) => {
              e.preventDefault();
              const val = e.currentTarget.batchId.value.trim();
              if (val) {
                window.location.href = `/verify/${encodeURIComponent(val)}`;
              }
            }}
            className="flex flex-col sm:flex-row items-stretch gap-3"
          >
            <div className="relative flex-1">
              <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-5 h-5 text-amber-700/60" />
              <input
                type="text"
                name="batchId"
                placeholder="Enter Batch ID (e.g. BATCH-2026-KVIC-001)"
                defaultValue="BATCH-2026-KVIC-001"
                className="w-full pl-11 pr-4 py-3.5 rounded-xl border border-amber-300/80 bg-[#FAF7F2] text-[#24140D] font-mono text-sm placeholder:text-amber-900/40 focus:outline-none focus:ring-2 focus:ring-[#CF840E] focus:border-transparent transition-all"
              />
            </div>
            <button
              type="submit"
              className="px-6 py-3.5 bg-[#24140D] hover:bg-[#3D2418] text-[#FDECB5] font-medium text-sm rounded-xl flex items-center justify-center space-x-2 shadow-md transition-colors"
            >
              <span>Verify Batch</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="mt-4 flex items-center justify-center space-x-6 text-xs text-amber-900/70">
            <span className="flex items-center space-x-1.5">
              <ShieldCheck className="w-4 h-4 text-emerald-700" />
              <span>Immutable Ledger</span>
            </span>
            <span className="flex items-center space-x-1.5">
              <Sprout className="w-4 h-4 text-amber-700" />
              <span>15% Beekeeper Royalty</span>
            </span>
          </div>
        </div>

        
        <div>
          <h2 className="text-xs font-mono uppercase tracking-wider text-amber-900/80 mb-3 px-1">
            Tap a Verified Harvest Batch to Inspect
          </h2>
          <div className="space-y-3">
            {sampleBatches.map((batch) => (
              <Link
                key={batch.batchId}
                href={`/verify/${batch.batchId}`}
                className="group block p-4 bg-white/70 hover:bg-white rounded-xl border border-amber-200/60 hover:border-[#CF840E] transition-all duration-200 shadow-sm hover:shadow-md"
              >
                <div className="flex items-start justify-between">
                  <div>
                    <div className="flex items-center space-x-2">
                      <span className="font-mono text-xs font-bold text-amber-900">
                        {batch.batchId}
                      </span>
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-100 text-emerald-800 border border-emerald-300/60">
                        VERIFIED
                      </span>
                    </div>
                    <h3 className="font-serif font-bold text-[#24140D] text-base mt-1 group-hover:text-[#CF840E] transition-colors">
                      {batch.harvest.floralSource}
                    </h3>
                    <p className="text-xs text-amber-900/80 mt-0.5">
                      {batch.beekeeper.name} · {batch.beekeeper.region}
                    </p>
                  </div>

                  <div className="text-right">
                    <span className="inline-block font-mono text-xs text-amber-800 bg-amber-100/70 px-2 py-1 rounded">
                      ₹{batch.royalty.royaltyPerKgINR}/kg royalty
                    </span>
                    <span className="block text-[10px] text-amber-900/60 mt-1">
                      Purity {batch.quality.purityScore}%
                    </span>
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      
      <footer className="w-full max-w-4xl mx-auto px-6 py-6 border-t border-amber-900/10 text-center text-xs text-amber-900/70">
        <p>
          Khadi and Village Industries Commission (KVIC) · Ministry of Micro, Small & Medium Enterprises
        </p>
        <p className="mt-1 font-mono text-[10px] text-amber-800/60">
          Smart India Hackathon 2026 · HoneyChain Traceability Protocol
        </p>
      </footer>
    </main>
  );
}
