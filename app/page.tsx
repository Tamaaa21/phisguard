"use client";

import React, { useState, useEffect } from "react";
import {
  Shield,
  ShieldAlert,
  ShieldCheck,
  AlertTriangle,
  Search,
  ExternalLink,
  Lock,
  Cpu,
  Layers,
  FileText,
  KeyRound,
  CheckCircle2,
  ChevronRight,
  Info,
  Clock,
  Activity,
  ArrowRight,
} from "lucide-react";
import { CheckResponse, ModelInfoResponse } from "@/lib/ml/types";

export default function Home() {
  const [urlInput, setUrlInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CheckResponse | null>(null);
  const [modelInfo, setModelInfo] = useState<ModelInfoResponse | null>(null);
  const [isOnline, setIsOnline] = useState(true);

  // Load Model Info on mount
  useEffect(() => {
    async function fetchModelData() {
      try {
        const res = await fetch("/api/model-info");
        if (res.ok) {
          const data = await res.json();
          setModelInfo(data);
          setIsOnline(true);
        }
      } catch (e) {
        console.warn("Could not fetch model info:", e);
        setIsOnline(false);
      }
    }
    fetchModelData();
  }, []);

  const handleScan = async (targetUrl?: string) => {
    const urlToScan = (targetUrl !== undefined ? targetUrl : urlInput).trim();
    if (!urlToScan) {
      setError("Silakan masukkan URL yang ingin diperiksa.");
      return;
    }

    setError(null);
    setResult(null);
    setLoading(true);

    try {
      const res = await fetch("/api/check", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlToScan }),
      });

      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || `Terjadi kesalahan (HTTP ${res.status})`);
      }

      setResult(data);
      // Smooth scroll to results
      setTimeout(() => {
        document.getElementById("result-anchor")?.scrollIntoView({ behavior: "smooth" });
      }, 100);
    } catch (err: any) {
      setError(err?.message || "Gagal memeriksa URL. Pastikan server berjalan.");
    } finally {
      setLoading(false);
    }
  };

  const exampleChips = [
    {
      label: "bankmandiri.co.id",
      url: "https://bankmandiri.co.id/personal",
      type: "safe",
      badge: "Aman",
    },
    {
      label: "paypal.com.verification...",
      url: "http://paypal.com.verification-security-update.xyz/login?token=98472",
      type: "danger",
      badge: "Waspada",
    },
    {
      label: "bca-login.bank-secure.id",
      url: "http://klikbca-login.bank-secure.id/masuk",
      type: "danger",
      badge: "Phishing Indo",
    },
  ];

  return (
    <div className="flex flex-col min-h-screen">
      {/* Site Header */}
      <header className="sticky top-0 z-50 backdrop-blur-md bg-[#090d16]/85 border-b border-slate-800/80">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 h-16 flex items-center justify-between">
          <a href="/" className="flex items-center gap-3 group">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-sky-500 to-blue-600 flex items-center justify-center shadow-lg shadow-sky-500/20 group-hover:scale-105 transition-transform">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-extrabold text-lg tracking-tight text-white">PhishGuard</span>
                <span className="text-[11px] font-semibold px-2 py-0.5 rounded-full bg-sky-500/15 text-sky-400 border border-sky-500/30">
                  ML v1
                </span>
              </div>
            </div>
          </a>

          <nav className="hidden md:flex items-center gap-6 text-sm font-medium text-slate-300">
            <a href="#scanner" className="hover:text-white transition-colors">Cek Link</a>
            <a href="#modus" className="hover:text-white transition-colors">Kasus Indonesia</a>
            <a href="#diagnostik" className="hover:text-white transition-colors">Pilar Deteksi</a>
            <a href="#tentang" className="hover:text-white transition-colors">Tentang Sistem</a>
          </nav>

          <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-900/90 border border-slate-800 text-xs text-slate-300 shadow-inner">
            <span className={`w-2 h-2 rounded-full ${isOnline ? "bg-emerald-400 animate-pulse" : "bg-rose-500"}`} />
            <span className="font-mono">
              Model v{modelInfo?.model_version || "1.0.0"} Online
            </span>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1">
        {/* Hero Interactive Scanner Section */}
        <section id="scanner" className="relative pt-12 pb-20 overflow-hidden">
          {/* Subtle background glow */}
          <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[300px] bg-sky-500/10 blur-[120px] rounded-full pointer-events-none -z-10" />

          <div className="max-w-4xl mx-auto px-4 sm:px-6">
            <div className="text-center mb-8">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-sky-950/60 border border-sky-800/50 text-sky-300 text-xs font-semibold mb-4">
                <Lock className="w-3.5 h-3.5 text-sky-400" />
                <span>Detektor Cepat & Aman (Zero-SSRF)</span>
              </div>

              <h1 className="text-3xl sm:text-5xl font-extrabold tracking-tight text-white mb-4 leading-tight">
                Periksa Keamanan Link <br className="hidden sm:inline" />
                <span className="bg-gradient-to-r from-sky-400 to-blue-500 bg-clip-text text-transparent">
                  Sebelum Anda Mengkliknya
                </span>
              </h1>

              <p className="text-slate-400 text-sm sm:text-base max-w-2xl mx-auto">
                Sistem mengevaluasi 49 fitur <em>lexical</em>, struktur domain, dan kemiripan merek secara <em>real-time</em> menggunakan model Machine Learning. Sistem <strong>tidak pernah</strong> membuka atau mengunduh situs sasaran.
              </p>
            </div>

            {/* Input Form Box */}
            <div className="bg-slate-900/80 backdrop-blur-xl border border-slate-800 p-3 sm:p-4 rounded-2xl shadow-2xl shadow-black/50">
              <form
                onSubmit={(e) => {
                  e.preventDefault();
                  handleScan();
                }}
                className="flex flex-col sm:flex-row gap-3"
              >
                <div className="relative flex-1">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                    <Search className="w-5 h-5" />
                  </div>
                  <input
                    type="text"
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    placeholder="Tempel URL di sini... (contoh: http://bca-verifikasi-akun.xyz/login)"
                    className="w-full pl-11 pr-4 py-3.5 rounded-xl bg-slate-950/80 border border-slate-700/80 text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 focus:ring-1 focus:ring-sky-500 text-sm font-mono transition-colors"
                    required
                  />
                </div>
                <button
                  type="submit"
                  disabled={loading}
                  className="px-6 py-3.5 rounded-xl bg-gradient-to-r from-sky-500 to-blue-600 hover:from-sky-400 hover:to-blue-500 text-white font-semibold text-sm transition-all shadow-lg shadow-sky-500/25 flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loading ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      <span>Menganalisis...</span>
                    </>
                  ) : (
                    <>
                      <span>Periksa Link</span>
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              {/* Quick Preset Chips */}
              <div className="mt-4 pt-3 border-t border-slate-800/60 flex flex-wrap items-center gap-2">
                <span className="text-xs font-medium text-slate-400 mr-1">Contoh Cepat:</span>
                {exampleChips.map((chip, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => {
                      setUrlInput(chip.url);
                      handleScan(chip.url);
                    }}
                    className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-slate-800/80 hover:bg-slate-700/80 border border-slate-700/60 text-xs font-mono text-slate-300 transition-colors"
                  >
                    <span
                      className={`text-[10px] font-bold px-1.5 py-0.2 rounded ${
                        chip.type === "safe"
                          ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                          : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
                      }`}
                    >
                      {chip.badge}
                    </span>
                    <span>{chip.label}</span>
                  </button>
                ))}
              </div>
            </div>

            {/* Error Message Alert */}
            {error && (
              <div className="mt-6 p-4 rounded-xl bg-rose-950/50 border border-rose-800/60 text-rose-300 flex items-center gap-3 text-sm">
                <AlertTriangle className="w-5 h-5 flex-shrink-0 text-rose-400" />
                <span>{error}</span>
              </div>
            )}

            {/* Loading Box */}
            {loading && (
              <div className="mt-8 p-8 rounded-2xl bg-slate-900/40 border border-slate-800 text-center flex flex-col items-center">
                <div className="w-10 h-10 border-3 border-sky-500/30 border-t-sky-400 rounded-full animate-spin mb-4" />
                <p className="font-semibold text-sky-300">Mengekstrak 49 Fitur & Menjalankan Model...</p>
                <p className="text-xs text-slate-400 mt-1">
                  Menganalisis struktur host, entropi karakter, kata kunci sensitif dwibahasa, dan jarak edit merek.
                </p>
              </div>
            )}

            {/* Result Display Box */}
            <div id="result-anchor" />
            {result && !loading && (
              <div className="mt-8 rounded-2xl bg-slate-900/90 border border-slate-800 overflow-hidden shadow-2xl">
                {/* Result Header */}
                <div
                  className={`p-6 border-b flex flex-col sm:flex-row sm:items-center justify-between gap-4 ${
                    result.risk_level === "high"
                      ? "bg-rose-950/40 border-rose-800/60"
                      : result.risk_level === "medium"
                      ? "bg-amber-950/40 border-amber-800/60"
                      : "bg-emerald-950/40 border-emerald-800/60"
                  }`}
                >
                  <div className="flex items-start sm:items-center gap-4">
                    <div
                      className={`p-3 rounded-xl border ${
                        result.risk_level === "high"
                          ? "bg-rose-500/20 border-rose-500/40 text-rose-400"
                          : result.risk_level === "medium"
                          ? "bg-amber-500/20 border-amber-500/40 text-amber-400"
                          : "bg-emerald-500/20 border-emerald-500/40 text-emerald-400"
                      }`}
                    >
                      {result.risk_level === "high" ? (
                        <ShieldAlert className="w-7 h-7" />
                      ) : result.risk_level === "medium" ? (
                        <AlertTriangle className="w-7 h-7" />
                      ) : (
                        <ShieldCheck className="w-7 h-7" />
                      )}
                    </div>
                    <div>
                      <h3
                        className={`text-lg sm:text-xl font-extrabold uppercase tracking-wide ${
                          result.risk_level === "high"
                            ? "text-rose-400"
                            : result.risk_level === "medium"
                            ? "text-amber-400"
                            : "text-emerald-400"
                        }`}
                      >
                        {result.risk_level === "high"
                          ? "RISIKO TINGGI (BAHAYA PHISHING)"
                          : result.risk_level === "medium"
                          ? "RISIKO SEDANG (MENCURIGAKAN)"
                          : "RISIKO RENDAH (TERLIHAT AMAN)"}
                      </h3>
                      <p className="text-xs sm:text-sm text-slate-300 mt-0.5">
                        {result.risk_level === "high"
                          ? "Tautan ini memiliki karakteristik kuat sebagai situs penipuan / pencurian kredensial."
                          : result.risk_level === "medium"
                          ? "Ditemukan beberapa indikator anomali pada struktur URL. Periksa keaslian domain secara teliti."
                          : "Tidak ditemukan pola manipulasi nama domain atau kata kunci penipuan mencurigakan."}
                      </p>
                    </div>
                  </div>

                  {/* Score badge */}
                  <div className="flex sm:flex-col items-center sm:items-end justify-between sm:justify-center border-t sm:border-t-0 border-slate-800 pt-3 sm:pt-0">
                    <div
                      className={`text-2xl sm:text-3xl font-extrabold font-mono ${
                        result.risk_level === "high"
                          ? "text-rose-400"
                          : result.risk_level === "medium"
                          ? "text-amber-400"
                          : "text-emerald-400"
                      }`}
                    >
                      {(result.score * 100).toFixed(1)}%
                    </div>
                    <div className="text-[11px] font-medium text-slate-400 uppercase tracking-wider">
                      Probabilitas Phishing
                    </div>
                  </div>
                </div>

                {/* Result Body */}
                <div className="p-6 space-y-6">
                  {/* Strict Plaintext URL Display (Zero Accidental Click) */}
                  <div className="p-4 rounded-xl bg-slate-950 border border-slate-800">
                    <div className="flex items-center justify-between text-xs text-slate-400 mb-1.5 font-medium">
                      <span>Tautan yang Diperiksa (Teks Biasa)</span>
                      <span className="inline-flex items-center gap-1 text-sky-400">
                        <Lock className="w-3 h-3" />
                        <span>Non-Clickable untuk Keamanan</span>
                      </span>
                    </div>
                    <div className="font-mono text-sm text-slate-200 break-all select-all select-text bg-slate-900/60 p-2.5 rounded-lg border border-slate-800">
                      {result.url}
                    </div>
                  </div>

                  {/* Diagnostic Findings */}
                  <div>
                    <h4 className="text-sm font-bold text-slate-200 mb-3 flex items-center gap-2">
                      <Activity className="w-4 h-4 text-sky-400" />
                      <span>Faktor Alasan & Temuan Diagnostik:</span>
                    </h4>
                    <ul className="space-y-2">
                      {result.reasons && result.reasons.length > 0 ? (
                        result.reasons.map((reason, idx) => (
                          <li
                            key={idx}
                            className="flex items-start gap-2.5 text-xs sm:text-sm text-slate-300 p-2.5 rounded-lg bg-slate-950/60 border border-slate-800/80"
                          >
                            <span
                              className={`p-1 rounded-md mt-0.5 ${
                                result.risk_level === "high"
                                  ? "text-rose-400 bg-rose-500/10"
                                  : result.risk_level === "medium"
                                  ? "text-amber-400 bg-amber-500/10"
                                  : "text-emerald-400 bg-emerald-500/10"
                              }`}
                            >
                              <ChevronRight className="w-3.5 h-3.5" />
                            </span>
                            <span>{reason}</span>
                          </li>
                        ))
                      ) : (
                        <li className="text-sm text-slate-400">Pola URL tidak menunjukkan anomali yang signifikan.</li>
                      )}
                    </ul>
                  </div>

                  {/* Disclaimer & Footer Info */}
                  <div className="pt-4 border-t border-slate-800/80 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 text-xs text-slate-400">
                    <div className="flex items-center gap-2">
                      <Info className="w-4 h-4 text-slate-500 flex-shrink-0" />
                      <span>{result.disclaimer}</span>
                    </div>
                    <div className="flex items-center gap-2 font-mono text-[11px] text-slate-400 flex-shrink-0">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700">
                        Model: {result.model_version}
                      </span>
                      {result.engine && (
                        <span className="px-2 py-0.5 rounded bg-sky-950/80 border border-sky-800/60 text-sky-300">
                          Next.js Native
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </section>

        {/* Section: Modus Phishing Nyata di Indonesia */}
        <section id="modus" className="py-16 bg-slate-950 border-t border-slate-850">
          <div className="max-w-6xl mx-auto px-4 sm:px-6">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-400 bg-sky-500/10 px-3 py-1 rounded-full border border-sky-500/20">
                Edukasi Keamanan Digital
              </span>
              <h2 className="text-2xl sm:text-4xl font-extrabold text-white mt-3 mb-3">
                Modus Phishing Nyata di Indonesia
              </h2>
              <p className="text-slate-400 text-sm">
                Pelaku penipuan sering meniru merek terpercaya dengan merekayasa subdomain atau memakai nama domain tiruan (<em>typosquatting</em>). Perhatikan perbedaannya:
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Case 1 */}
              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
                <div>
                  <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">Perbankan Digital</span>
                  <h4 className="text-lg font-bold text-white mt-1 mb-4">Modus Pembaruan Akun Bank</h4>
                  <div className="space-y-2 text-xs font-mono">
                    <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 text-emerald-300 flex items-center justify-between">
                      <span className="truncate">https://www.klikbca.com/</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-500/20 rounded text-emerald-400 border border-emerald-500/30 flex-shrink-0">
                        Resmi
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/40 text-rose-300 flex items-center justify-between">
                      <span className="truncate">http://klikbca-login.bank-secure.id/</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-rose-500/20 rounded text-rose-400 border border-rose-500/30 flex-shrink-0">
                        Jebakan
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-400 mt-4 pt-3 border-t border-slate-800">
                  <strong className="text-slate-300">Ciri:</strong> Nama bank disematkan sebagai kata kunci pada domain baru yang tidak terdaftar atas nama bank resmi.
                </p>
              </div>

              {/* Case 2 */}
              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
                <div>
                  <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">Dompet Digital / E-Wallet</span>
                  <h4 className="text-lg font-bold text-white mt-1 mb-4">Modus Klaim Saldo & Hadiah</h4>
                  <div className="space-y-2 text-xs font-mono">
                    <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 text-emerald-300 flex items-center justify-between">
                      <span className="truncate">https://www.dana.id/</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-500/20 rounded text-emerald-400 border border-emerald-500/30 flex-shrink-0">
                        Resmi
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/40 text-rose-300 flex items-center justify-between">
                      <span className="truncate">http://dana-id.klaim-saldo.xyz/bayar</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-rose-500/20 rounded text-rose-400 border border-rose-500/30 flex-shrink-0">
                        Jebakan
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-400 mt-4 pt-3 border-t border-slate-800">
                  <strong className="text-slate-300">Ciri:</strong> Memakai TLD murah (.xyz/.top) dan kata iming-iming hadiah atau saldo darurat.
                </p>
              </div>

              {/* Case 3 */}
              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
                <div>
                  <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">Jasa Ekspedisi / Kurir</span>
                  <h4 className="text-lg font-bold text-white mt-1 mb-4">Modus Lacak Paket Tertahan</h4>
                  <div className="space-y-2 text-xs font-mono">
                    <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 text-emerald-300 flex items-center justify-between">
                      <span className="truncate">https://www.jne.co.id/</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-500/20 rounded text-emerald-400 border border-emerald-500/30 flex-shrink-0">
                        Resmi
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/40 text-rose-300 flex items-center justify-between">
                      <span className="truncate">http://lacak-paket-jne.tracking-resikirim.com/</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-rose-500/20 rounded text-rose-400 border border-rose-500/30 flex-shrink-0">
                        Jebakan
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-400 mt-4 pt-3 border-t border-slate-800">
                  <strong className="text-slate-300">Ciri:</strong> Menggiring korban untuk memasukkan nomor telepon dan kode OTP SMS / unduh file APK berbahaya.
                </p>
              </div>

              {/* Case 4 */}
              <div className="p-6 rounded-2xl bg-slate-900 border border-slate-800 hover:border-slate-700 transition-colors flex flex-col justify-between">
                <div>
                  <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider">Marketplace & E-Commerce</span>
                  <h4 className="text-lg font-bold text-white mt-1 mb-4">Modus Undian Toko / Kupon Promo</h4>
                  <div className="space-y-2 text-xs font-mono">
                    <div className="p-3 rounded-lg bg-emerald-950/30 border border-emerald-800/40 text-emerald-300 flex items-center justify-between">
                      <span className="truncate">https://shopee.co.id/</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-emerald-500/20 rounded text-emerald-400 border border-emerald-500/30 flex-shrink-0">
                        Resmi
                      </span>
                    </div>
                    <div className="p-3 rounded-lg bg-rose-950/30 border border-rose-800/40 text-rose-300 flex items-center justify-between">
                      <span className="truncate">http://shopee-undian-pemenang.top/klaim</span>
                      <span className="text-[10px] font-bold px-1.5 py-0.5 bg-rose-500/20 rounded text-rose-400 border border-rose-500/30 flex-shrink-0">
                        Jebakan
                      </span>
                    </div>
                  </div>
                </div>
                <p className="text-xs text-slate-400 mt-4 pt-3 border-t border-slate-800">
                  <strong className="text-slate-300">Ciri:</strong> Menggunakan domain tidak lazim dengan menyisipkan kata 'undian' dan 'pemenang'.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Section: 4 ML Detection Pillars */}
        <section id="diagnostik" className="py-16 bg-[#090d16] border-t border-slate-800">
          <div className="max-w-6xl mx-auto px-4 sm:px-6">
            <div className="text-center max-w-2xl mx-auto mb-12">
              <span className="text-xs font-bold uppercase tracking-wider text-sky-400 bg-sky-500/10 px-3 py-1 rounded-full border border-sky-500/20">
                Arsitektur Machine Learning
              </span>
              <h2 className="text-2xl sm:text-4xl font-extrabold text-white mt-3 mb-3">
                4 Pilar Fitur yang Dianalisis
              </h2>
              <p className="text-slate-400 text-sm">
                Model LightGBM terlatih mengevaluasi 49 indikator statistik dan struktural tanpa perlu membuka tautan sasaran.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <div className="w-12 h-12 rounded-xl bg-sky-500/10 border border-sky-500/30 text-sky-400 flex items-center justify-center mb-4">
                  <Cpu className="w-6 h-6" />
                </div>
                <h4 className="font-bold text-white mb-2">1. Karakteristik Lexical</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Panjang total URL, panjang hostname dan path, jumlah tanda hubung (-), titik (.), rasio digit angka, serta tingkat keacakan karakter (Shannon Entropy).
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <div className="w-12 h-12 rounded-xl bg-blue-500/10 border border-blue-500/30 text-blue-400 flex items-center justify-center mb-4">
                  <Layers className="w-6 h-6" />
                </div>
                <h4 className="font-bold text-white mb-2">2. Deteksi Merek & Typosquatting</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Jarak edit (Levenshtein) terhadap 32 merek teratas global dan Indonesia, serta deteksi penipuan nama merek yang ditaruh di subdomain.
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 flex items-center justify-center mb-4">
                  <Lock className="w-6 h-6" />
                </div>
                <h4 className="font-bold text-white mb-2">3. Struktur Host & Keamanan</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Inspeksi protokol HTTPS, pemakaian alamat IP langsung (IPv4/hex/integer), layanan pemendek tautan (URL Shortener), dan karakter Punycode (homograph).
                </p>
              </div>

              <div className="p-6 rounded-2xl bg-slate-900/60 border border-slate-800">
                <div className="w-12 h-12 rounded-xl bg-amber-500/10 border border-amber-500/30 text-amber-400 flex items-center justify-center mb-4">
                  <KeyRound className="w-6 h-6" />
                </div>
                <h4 className="font-bold text-white mb-2">4. Kata Kunci Sensitif (Bilingual)</h4>
                <p className="text-xs text-slate-400 leading-relaxed">
                  Kamus sensitif mencakup kata sandi, akun, verifikasi, perbankan, saldo, darurat, pemblokiran, dan bayar dalam Bahasa Indonesia dan Inggris.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Section: Tentang Sistem & Evaluasi */}
        <section id="tentang" className="py-16 bg-slate-950 border-t border-slate-800">
          <div className="max-w-6xl mx-auto px-4 sm:px-6">
            <div className="p-8 sm:p-12 rounded-3xl bg-slate-900/90 border border-slate-800 grid grid-cols-1 md:grid-cols-2 gap-8 sm:gap-12">
              <div>
                <h3 className="text-xl font-bold text-white mb-4">Cara Kerja PhishGuard</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  PhishGuard dirancang sebagai lapis pertahanan dini terhadap kejahatan siber berbasis tautan palsu.
                  Model telah dilatih dan divalidasi pada ribuan domain independen dengan metodologi pemisahan domain ketat (<em>zero domain leakage</em>).
                </p>
                <div className="mt-6 space-y-3">
                  <div className="flex items-center gap-3 text-sm text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    <span><strong>Akurasi Test Set:</strong> 88.11% pada 1.690 sampel uji independen.</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    <span><strong>Area Under Curve (ROC-AUC):</strong> 0.9519.</span>
                  </div>
                  <div className="flex items-center gap-3 text-sm text-slate-300">
                    <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                    <span><strong>Kecepatan Inferensi:</strong> &lt; 5 ms per URL (pure JavaScript/TypeScript).</span>
                  </div>
                </div>
              </div>

              <div>
                <h3 className="text-xl font-bold text-white mb-4">Keterbatasan & Panduan Aman</h3>
                <p className="text-sm text-slate-400 leading-relaxed">
                  Sebagai sistem deteksi dini yang mengutamakan kecepatan dan keselamatan (tidak membuka halaman target untuk menghindari risiko SSRF):
                </p>
                <ul className="mt-6 space-y-3 text-sm text-slate-400">
                  <li className="flex items-start gap-2">
                    <span className="text-sky-400">•</span>
                    <span>Model hanya mengevaluasi pola string URL, bukan isi halaman atau sertifikat TLS terkini.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-sky-400">•</span>
                    <span>Situs sah yang baru dibuat atau memiliki subdomain kompleks terkadang dapat diklasifikasikan sebagai <em>Medium Risk</em>.</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-sky-400">•</span>
                    <span><strong>Jangan pernah</strong> membagikan kode OTP, PIN perbankan, atau password pada link dari pengirim yang tidak dikenal.</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
      </main>

      {/* Site Footer */}
      <footer className="border-t border-slate-800 bg-[#090d16] py-10">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 flex flex-col md:flex-row items-center justify-between gap-6 text-xs text-slate-400">
          <div className="flex flex-col items-center md:items-start gap-1">
            <div className="font-bold text-slate-300 flex items-center gap-2">
              <Shield className="w-4 h-4 text-sky-400" />
              <span>PhishGuard — ML URL Phishing Detector (Next.js Edition)</span>
            </div>
            <p className="text-slate-400 text-center md:text-left">
              Tautan yang dimasukkan hanya dianalisis untuk inferensi dan tidak disimpan secara permanen demi menjaga privasi pengguna.
            </p>
          </div>

          <div className="text-center md:text-right space-y-1 font-mono text-[11px] text-slate-400">
            <div>&copy; 2026 PhishGuard. Riset Keamanan Siber Indonesia.</div>
            <div className="text-slate-400">LightGBM Tabular Classifier v1.0.0 (TypeScript Native Engine)</div>
          </div>
        </div>
      </footer>
    </div>
  );
}
