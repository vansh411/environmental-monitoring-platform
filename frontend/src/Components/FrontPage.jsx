import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

const style = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #050a08;
    --surface: #0b140f;
    --surface2: #101e14;
    --border: rgba(74, 222, 128, 0.12);
    --green: #4ade80;
    --green-dim: #22c55e;
    --green-glow: rgba(74, 222, 128, 0.18);
    --amber: #fbbf24;
    --blue: #38bdf8;
    --text: #e2f5e8;
    --muted: #4b6b54;
    --font-display: 'Syne', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }

  .fp-root {
    font-family: var(--font-display);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
    position: relative;
  }

  /* ─── Animated grid background ─── */
  .fp-grid-bg {
    position: fixed;
    inset: 0;
    background-image:
      linear-gradient(rgba(74,222,128,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(74,222,128,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none;
    z-index: 0;
  }

  .fp-noise {
    position: fixed;
    inset: 0;
    background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E");
    opacity: 0.4;
    pointer-events: none;
    z-index: 0;
  }

  .fp-glow-orb {
    position: fixed;
    width: 600px;
    height: 600px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(74,222,128,0.06) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    top: -100px;
    left: -100px;
    animation: orbFloat 12s ease-in-out infinite alternate;
  }
  .fp-glow-orb2 {
    position: fixed;
    width: 500px;
    height: 500px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(56,189,248,0.05) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
    bottom: 0;
    right: -100px;
    animation: orbFloat2 15s ease-in-out infinite alternate;
  }

  @keyframes orbFloat {
    from { transform: translate(0,0); }
    to { transform: translate(80px, 60px); }
  }
  @keyframes orbFloat2 {
    from { transform: translate(0,0); }
    to { transform: translate(-60px, -40px); }
  }

  /* ─── NAV ─── */
  .fp-nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    z-index: 100;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 48px;
    background: rgba(5,10,8,0.7);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
  }

  .fp-logo {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 800;
    font-size: 1.1rem;
    letter-spacing: -0.02em;
    color: var(--text);
  }

  .fp-logo-icon {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, var(--green), var(--green-dim));
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
    box-shadow: 0 0 20px var(--green-glow);
  }

  .fp-nav-links {
    display: flex;
    gap: 32px;
    list-style: none;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    letter-spacing: 0.05em;
    color: var(--muted);
  }

  .fp-nav-links li {
    cursor: pointer;
    transition: color 0.2s;
    text-transform: uppercase;
  }
  .fp-nav-links li:hover { color: var(--green); }

  .fp-nav-cta {
    background: transparent;
    border: 1px solid var(--green);
    color: var(--green);
    font-family: var(--font-mono);
    font-size: 0.75rem;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 9px 22px;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
  }
  .fp-nav-cta:hover {
    background: var(--green);
    color: var(--bg);
    box-shadow: 0 0 24px var(--green-glow);
  }

  /* ─── HERO ─── */
  .fp-hero {
    position: relative;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    padding: 180px 24px 100px;
  }

  .fp-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--green);
    border: 1px solid var(--border);
    background: rgba(74,222,128,0.06);
    padding: 6px 16px;
    border-radius: 999px;
    margin-bottom: 32px;
    animation: fadeUp 0.7s ease both;
  }

  .fp-badge-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: pulse 2s infinite;
  }

  @keyframes pulse {
    0%, 100% { opacity: 1; transform: scale(1); }
    50% { opacity: 0.5; transform: scale(0.85); }
  }

  .fp-hero-title {
    font-size: clamp(3rem, 7vw, 6.5rem);
    font-weight: 800;
    line-height: 1.0;
    letter-spacing: -0.03em;
    margin-bottom: 24px;
    animation: fadeUp 0.7s 0.1s ease both;
  }

  .fp-hero-title .accent {
    background: linear-gradient(135deg, var(--green) 0%, var(--blue) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }

  .fp-hero-sub {
    max-width: 560px;
    font-family: var(--font-mono);
    font-size: 0.95rem;
    font-weight: 300;
    color: var(--muted);
    line-height: 1.7;
    margin-bottom: 48px;
    animation: fadeUp 0.7s 0.2s ease both;
  }

  .fp-hero-actions {
    display: flex;
    gap: 16px;
    animation: fadeUp 0.7s 0.3s ease both;
  }

  .fp-btn-primary {
    background: var(--green);
    color: var(--bg);
    font-family: var(--font-mono);
    font-size: 0.82rem;
    font-weight: 500;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 14px 32px;
    border-radius: 8px;
    border: none;
    cursor: pointer;
    transition: all 0.25s;
    box-shadow: 0 0 32px var(--green-glow);
  }
  .fp-btn-primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 0 48px rgba(74,222,128,0.35);
  }

  .fp-btn-ghost {
    background: transparent;
    color: var(--muted);
    font-family: var(--font-mono);
    font-size: 0.82rem;
    font-weight: 400;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    padding: 14px 32px;
    border-radius: 8px;
    border: 1px solid rgba(74,222,128,0.2);
    cursor: pointer;
    transition: all 0.25s;
  }
  .fp-btn-ghost:hover { color: var(--text); border-color: rgba(74,222,128,0.5); }

  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
  }

  /* ─── STATS BAR ─── */
  .fp-stats {
    position: relative;
    z-index: 10;
    display: flex;
    justify-content: center;
    gap: 0;
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    background: rgba(11,20,15,0.5);
    backdrop-filter: blur(8px);
    animation: fadeUp 0.7s 0.4s ease both;
  }

  .fp-stat-item {
    flex: 1;
    max-width: 240px;
    padding: 28px 32px;
    border-right: 1px solid var(--border);
    text-align: center;
  }
  .fp-stat-item:last-child { border-right: none; }

  .fp-stat-value {
    font-size: 2rem;
    font-weight: 800;
    color: var(--green);
    letter-spacing: -0.02em;
    line-height: 1;
    margin-bottom: 6px;
  }

  .fp-stat-label {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
  }

  /* ─── FEATURES ─── */
  .fp-features {
    position: relative;
    z-index: 10;
    padding: 100px 48px;
    max-width: 1200px;
    margin: 0 auto;
  }

  .fp-section-label {
    font-family: var(--font-mono);
    font-size: 0.72rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--green);
    margin-bottom: 16px;
  }

  .fp-section-title {
    font-size: 2.8rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.1;
    max-width: 520px;
    margin-bottom: 64px;
  }

  .fp-features-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 2px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
  }

  .fp-feature-card {
    background: var(--surface);
    padding: 36px;
    transition: background 0.3s;
    cursor: default;
    position: relative;
    overflow: hidden;
  }
  .fp-feature-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--green), transparent);
    opacity: 0;
    transition: opacity 0.3s;
  }
  .fp-feature-card:hover { background: var(--surface2); }
  .fp-feature-card:hover::before { opacity: 1; }

  .fp-feature-icon {
    font-size: 2rem;
    margin-bottom: 20px;
    display: block;
  }

  .fp-feature-name {
    font-size: 1.05rem;
    font-weight: 700;
    letter-spacing: -0.01em;
    margin-bottom: 10px;
  }

  .fp-feature-desc {
    font-family: var(--font-mono);
    font-size: 0.78rem;
    line-height: 1.7;
    color: var(--muted);
  }

  .fp-feature-tag {
    display: inline-block;
    margin-top: 16px;
    font-family: var(--font-mono);
    font-size: 0.65rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 4px;
    background: var(--green-glow);
    color: var(--green);
  }

  /* ─── TERMINAL BLOCK ─── */
  .fp-terminal-section {
    position: relative;
    z-index: 10;
    padding: 0 48px 100px;
    max-width: 1200px;
    margin: 0 auto;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 64px;
    align-items: center;
  }

  .fp-terminal {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
    font-family: var(--font-mono);
    font-size: 0.78rem;
    box-shadow: 0 32px 80px rgba(0,0,0,0.5), 0 0 0 1px var(--border);
  }

  .fp-terminal-bar {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px 16px;
    background: rgba(255,255,255,0.03);
    border-bottom: 1px solid var(--border);
  }

  .fp-dot { width: 10px; height: 10px; border-radius: 50%; }
  .fp-dot-r { background: #ff5f57; }
  .fp-dot-y { background: #febc2e; }
  .fp-dot-g { background: #28c840; }

  .fp-terminal-title {
    flex: 1;
    text-align: center;
    color: var(--muted);
    font-size: 0.7rem;
    letter-spacing: 0.05em;
  }

  .fp-terminal-body {
    padding: 20px;
    line-height: 1.9;
  }

  .fp-line-muted { color: var(--muted); }
  .fp-line-green { color: var(--green); }
  .fp-line-amber { color: var(--amber); }
  .fp-line-blue { color: var(--blue); }
  .fp-line-white { color: var(--text); }

  .fp-cursor {
    display: inline-block;
    width: 8px;
    height: 14px;
    background: var(--green);
    animation: blink 1s step-end infinite;
    vertical-align: middle;
    margin-left: 2px;
  }
  @keyframes blink { 50% { opacity: 0; } }

  .fp-terminal-info h3 {
    font-size: 2rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    line-height: 1.2;
    margin-bottom: 16px;
  }

  .fp-terminal-info p {
    font-family: var(--font-mono);
    font-size: 0.82rem;
    line-height: 1.8;
    color: var(--muted);
    margin-bottom: 28px;
  }

  .fp-chip-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }

  .fp-chip {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    letter-spacing: 0.06em;
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid var(--border);
    color: var(--muted);
    text-transform: uppercase;
  }

  /* ─── WORKFLOW ─── */
  .fp-workflow {
    position: relative;
    z-index: 10;
    padding: 100px 48px;
    background: var(--surface);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
  }

  .fp-workflow-inner {
    max-width: 900px;
    margin: 0 auto;
  }

  .fp-steps {
    display: flex;
    flex-direction: column;
    gap: 0;
    margin-top: 48px;
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
  }

  .fp-step {
    display: flex;
    align-items: flex-start;
    gap: 24px;
    padding: 28px 32px;
    border-bottom: 1px solid var(--border);
    background: var(--bg);
    transition: background 0.2s;
  }
  .fp-step:last-child { border-bottom: none; }
  .fp-step:hover { background: var(--surface2); }

  .fp-step-num {
    font-family: var(--font-mono);
    font-size: 0.7rem;
    color: var(--green);
    letter-spacing: 0.1em;
    background: var(--green-glow);
    border: 1px solid rgba(74,222,128,0.3);
    border-radius: 6px;
    padding: 6px 10px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .fp-step-title {
    font-size: 1rem;
    font-weight: 700;
    margin-bottom: 6px;
  }

  .fp-step-desc {
    font-family: var(--font-mono);
    font-size: 0.77rem;
    color: var(--muted);
    line-height: 1.7;
  }

  /* ─── CTA ─── */
  .fp-cta {
    position: relative;
    z-index: 10;
    padding: 120px 48px;
    text-align: center;
  }

  .fp-cta-box {
    max-width: 680px;
    margin: 0 auto;
    border: 1px solid var(--border);
    border-radius: 20px;
    padding: 72px 48px;
    background: var(--surface);
    position: relative;
    overflow: hidden;
  }

  .fp-cta-box::before {
    content: '';
    position: absolute;
    top: -1px; left: 20%; right: 20%;
    height: 2px;
    background: linear-gradient(90deg, transparent, var(--green), transparent);
  }

  .fp-cta-box h2 {
    font-size: 2.6rem;
    font-weight: 800;
    letter-spacing: -0.02em;
    margin-bottom: 16px;
    line-height: 1.1;
  }

  .fp-cta-box p {
    font-family: var(--font-mono);
    font-size: 0.85rem;
    color: var(--muted);
    margin-bottom: 36px;
    line-height: 1.7;
  }

  /* ─── FOOTER ─── */
  .fp-footer {
    position: relative;
    z-index: 10;
    border-top: 1px solid var(--border);
    padding: 28px 48px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: var(--font-mono);
    font-size: 0.72rem;
    color: var(--muted);
  }

  @media (max-width: 900px) {
    .fp-nav { padding: 16px 20px; }
    .fp-nav-links { display: none; }
    .fp-hero { padding: 140px 20px 80px; }
    .fp-features-grid { grid-template-columns: 1fr; }
    .fp-terminal-section { grid-template-columns: 1fr; padding: 0 20px 80px; }
    .fp-features { padding: 80px 20px; }
    .fp-stats { flex-wrap: wrap; }
    .fp-stat-item { min-width: 150px; }
    .fp-footer { flex-direction: column; gap: 12px; text-align: center; }
  }
`;

const features = [
  {
    icon: "🌲",
    name: "Deforestation Tracking",
    desc: "Monitor forest cover loss in near-real-time using multi-spectral Sentinel-2 bands with sub-hectare resolution.",
    tag: "Active Monitoring",
  },
  {
    icon: "🏙️",
    name: "Urban Expansion Analysis",
    desc: "Detect impervious surface growth, classify urban typologies, and map sprawl trajectories across city boundaries.",
    tag: "Change Detection",
  },
  {
    icon: "🌾",
    name: "Agricultural Monitoring",
    desc: "Track crop health, rotation patterns, and irrigation anomalies using NDVI time-series and ViT classification.",
    tag: "Seasonal Analysis",
  },
  {
    icon: "🛰️",
    name: "Sentinel-2 Integration",
    desc: "Direct ESA Copernicus API pipeline with automated cloud masking, atmospheric correction, and band compositing.",
    tag: "10m Resolution",
  },
  {
    icon: "⚡",
    name: "Real-time Dashboard",
    desc: "Live geospatial visualizations with alert thresholds, anomaly scoring, and exportable change reports.",
    tag: "Live Data",
  },
  {
    icon: "🧠",
    name: "Vision Transformer AI",
    desc: "Fine-tuned ViT model on EuroSAT land cover dataset achieving 98.6% classification accuracy across 10 classes.",
    tag: "98.6% Accuracy",
  },
];

const steps = [
  { num: "01", title: "Satellite Data Ingestion", desc: "Sentinel-2 Level-2A imagery is automatically fetched via Copernicus Open Access Hub at configurable intervals, with cloud coverage filtering and geometric correction applied." },
  { num: "02", title: "Preprocessing Pipeline", desc: "Multi-spectral bands are normalized, cloud-masked using SCL band, and co-registered against baseline imagery to ensure temporal consistency before analysis." },
  { num: "03", title: "ViT Classification", desc: "Preprocessed 64×64 patches are passed through the Vision Transformer model, producing land cover class probabilities for each spatial unit in the scene." },
  { num: "04", title: "Change Detection & Alerting", desc: "Class maps are differenced against historical baselines. Significant deviations trigger configurable alerts delivered via webhook, email, or the real-time dashboard." },
];

export default function FrontPage() {
  const navigate = useNavigate();
  const goToClassifier = () => navigate("/classifier");
  const [counter, setCounter] = useState({ area: 0, scenes: 0, alerts: 0 });

  useEffect(() => {
    const targets = { area: 2847, scenes: 14902, alerts: 389 };
    const duration = 1800;
    const steps = 60;
    const interval = duration / steps;
    let step = 0;
    const timer = setInterval(() => {
      step++;
      const progress = step / steps;
      const ease = 1 - Math.pow(1 - progress, 3);
      setCounter({
        area: Math.round(targets.area * ease),
        scenes: Math.round(targets.scenes * ease),
        alerts: Math.round(targets.alerts * ease),
      });
      if (step >= steps) clearInterval(timer);
    }, interval);
    return () => clearInterval(timer);
  }, []);

  return (
    <>
      <style>{style}</style>
      <div className="fp-root">
        <div className="fp-grid-bg" />
        <div className="fp-noise" />
        <div className="fp-glow-orb" />
        <div className="fp-glow-orb2" />

        {/* NAV */}
        <nav className="fp-nav">
          <div className="fp-logo">
            <div className="fp-logo-icon"></div>
            GeoSentinel
          </div>
          <ul className="fp-nav-links">
            <li>Platform</li>
            <li>Monitoring</li>
            <li>API</li>
            <li>Research</li>
          </ul>
          <button className="fp-nav-cta" onClick={goToClassifier}>
            Open Dashboard →
          </button>
        </nav>

        {/* HERO */}
        <section className="fp-hero">
          <div className="fp-badge">
            <span className="fp-badge-dot" />
            Sentinel-2 Live · ESA Copernicus
          </div>
          <h1 className="fp-hero-title">
            Environmental<br />
            <span className="accent">Intelligence</span><br />
            at Scale
          </h1>
          <p className="fp-hero-sub">
            AI-powered land use change detection using Vision Transformers and multi-spectral satellite imagery. Monitor deforestation, urban growth, and agricultural shifts globally.
          </p>
          <div className="fp-hero-actions">
            <button className="fp-btn-primary" onClick={goToClassifier}>
              Launch Classifier
            </button>
            <button className="fp-btn-ghost">View Documentation</button>
          </div>
        </section>

        {/* STATS */}
        <div className="fp-stats">
          <div className="fp-stat-item">
            <div className="fp-stat-value">{counter.area.toLocaleString()}</div>
            <div className="fp-stat-label">km² Monitored Today</div>
          </div>
          <div className="fp-stat-item">
            <div className="fp-stat-value">{counter.scenes.toLocaleString()}</div>
            <div className="fp-stat-label">Scenes Processed</div>
          </div>
          <div className="fp-stat-item">
            <div className="fp-stat-value">{counter.alerts.toLocaleString()}</div>
            <div className="fp-stat-label">Change Alerts Fired</div>
          </div>
          <div className="fp-stat-item">
            <div className="fp-stat-value">98.6%</div>
            <div className="fp-stat-label">Model Accuracy</div>
          </div>
        </div>

        {/* FEATURES */}
        <section className="fp-features">
        
          <h2 className="fp-section-title">Everything you need to monitor Earth's surface</h2>
          <div className="fp-features-grid">
            {features.map((f) => (
              <div className="fp-feature-card" key={f.name}>
                <span className="fp-feature-icon">{f.icon}</span>
                <div className="fp-feature-name">{f.name}</div>
                <div className="fp-feature-desc">{f.desc}</div>
                <span className="fp-feature-tag">{f.tag}</span>
              </div>
            ))}
          </div>
        </section>

        {/* TERMINAL SECTION */}
        <section className="fp-terminal-section">
          <div className="fp-terminal">
            <div className="fp-terminal-bar">
              <div className="fp-dot fp-dot-r" />
              <div className="fp-dot fp-dot-y" />
              <div className="fp-dot fp-dot-g" />
              <div className="fp-terminal-title">geosentinel — inference.py</div>
            </div>
            <div className="fp-terminal-body">
              <div className="fp-line-muted"># Loading ViT model checkpoint</div>
              <div className="fp-line-green">✓ Model loaded &nbsp;<span className="fp-line-muted">ViT-B/16 · EuroSAT</span></div>
              <div className="fp-line-muted"># Fetching Sentinel-2 scene</div>
              <div className="fp-line-amber">→ T30UXC_20250221T105901</div>
              <div className="fp-line-muted"># Preprocessing bands [B02, B03, B04, B08]</div>
              <div className="fp-line-green">✓ Cloud mask applied &nbsp;<span className="fp-line-muted">CCov: 4.2%</span></div>
              <div className="fp-line-muted"># Running patch-wise inference</div>
              <div className="fp-line-green">✓ 2,048 patches classified</div>
              <div>&nbsp;</div>
              <div className="fp-line-muted">Classification Results:</div>
              <div><span className="fp-line-blue">Forest</span> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;→ <span className="fp-line-green">34.2%</span></div>
              <div><span className="fp-line-blue">Industrial</span> &nbsp;&nbsp;→ <span className="fp-line-amber">18.7%</span></div>
              <div><span className="fp-line-blue">Residential</span> →  <span className="fp-line-green">22.1%</span></div>
              <div><span className="fp-line-blue">AnnualCrop</span>  → <span className="fp-line-green">25.0%</span></div>
              <div>&nbsp;</div>
              <div className="fp-line-amber">⚠ Change alert: -12.4% Forest cover</div>
              <div className="fp-line-muted">$ <span className="fp-cursor" /></div>
            </div>
          </div>
          <div className="fp-terminal-info">
            <div className="fp-section-label">// under the hood</div>
            <h3>ViT-powered land cover classification</h3>
            <p>
              Our pipeline ingests raw Sentinel-2 imagery and runs each scene through a fine-tuned Vision Transformer, producing pixel-accurate land cover maps with confidence scores — all in under 90 seconds.
            </p>
            <div className="fp-chip-list">
              <span className="fp-chip">PyTorch</span>
              <span className="fp-chip">HuggingFace</span>
              <span className="fp-chip">Sentinel-2</span>
              <span className="fp-chip">EuroSAT</span>
              <span className="fp-chip">GDAL</span>
              <span className="fp-chip">GeoJSON</span>
            </div>
          </div>
        </section>

        {/* WORKFLOW */}
        <section className="fp-workflow">
          <div className="fp-workflow-inner">
            <div className="fp-section-label">// how it works</div>
            <h2 className="fp-section-title" style={{ fontSize: "2.2rem", marginBottom: 0 }}>
              From raw satellite to actionable intelligence
            </h2>
            <div className="fp-steps">
              {steps.map((s) => (
                <div className="fp-step" key={s.num}>
                  <span className="fp-step-num">{s.num}</span>
                  <div>
                    <div className="fp-step-title">{s.title}</div>
                    <div className="fp-step-desc">{s.desc}</div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="fp-cta">
          <div className="fp-cta-box">
            <h2>Start monitoring the planet</h2>
            <p>Upload a satellite image and get AI land cover classification in seconds. No setup required.</p>
            <button className="fp-btn-primary" onClick={goToClassifier} style={{ fontSize: "0.88rem" }}>
              Open Land Cover Classifier →
            </button>
          </div>
        </section>

        {/* FOOTER */}
        <footer className="fp-footer">
          <div>© 2025 GeoSentinel · Environmental Intelligence Platform</div>
          <div>Powered by Sentinel-2 · ESA Copernicus · Vision Transformers</div>
        </footer>
      </div>
    </>
  );
}
