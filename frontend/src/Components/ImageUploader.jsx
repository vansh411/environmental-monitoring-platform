import React, { useState, useRef } from "react";
import axios from "axios";

// ─── Styles ───────────────────────────────────────────────────────────────────
const style = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=JetBrains+Mono:wght@300;400;500&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  :root {
    --bg: #050a08;
    --surface: #0b140f;
    --surface2: #101e14;
    --border: rgba(74, 222, 128, 0.12);
    --border-hover: rgba(74, 222, 128, 0.35);
    --green: #4ade80;
    --green-dim: #22c55e;
    --green-glow: rgba(74, 222, 128, 0.18);
    --amber: #fbbf24;
    --red: #f87171;
    --blue: #38bdf8;
    --text: #e2f5e8;
    --muted: #4b6b54;
    --font-display: 'Syne', sans-serif;
    --font-mono: 'JetBrains Mono', monospace;
  }

  .cl-root {
    font-family: var(--font-display);
    background: var(--bg);
    color: var(--text);
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    position: relative;
    overflow-x: hidden;
  }

  /* ─── Background ─── */
  .cl-grid-bg {
    position: fixed; inset: 0;
    background-image:
      linear-gradient(rgba(74,222,128,0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(74,222,128,0.04) 1px, transparent 1px);
    background-size: 48px 48px;
    pointer-events: none; z-index: 0;
  }
  .cl-glow {
    position: fixed;
    width: 500px; height: 500px; border-radius: 50%;
    background: radial-gradient(circle, rgba(74,222,128,0.05) 0%, transparent 70%);
    top: -80px; left: -80px;
    pointer-events: none; z-index: 0;
  }

  /* ─── Nav ─── */
  .cl-nav {
    position: sticky; top: 0; z-index: 100;
    display: flex; align-items: center; justify-content: space-between;
    padding: 16px 40px;
    background: rgba(5,10,8,0.8);
    backdrop-filter: blur(16px);
    border-bottom: 1px solid var(--border);
  }
  .cl-nav-logo {
    display: flex; align-items: center; gap: 10px;
    font-weight: 800; font-size: 1rem; letter-spacing: -0.02em;
    cursor: pointer; transition: opacity 0.2s;
  }
  .cl-nav-logo:hover { opacity: 0.8; }
  .cl-logo-icon {
    width: 30px; height: 30px; border-radius: 7px;
    background: linear-gradient(135deg, var(--green), var(--green-dim));
    display: flex; align-items: center; justify-content: center;
    font-size: 14px; box-shadow: 0 0 16px var(--green-glow);
  }
  .cl-nav-back {
    font-family: var(--font-mono);
    font-size: 0.72rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--muted); background: transparent;
    border: 1px solid var(--border); border-radius: 6px;
    padding: 7px 16px; cursor: pointer; transition: all 0.2s;
  }
  .cl-nav-back:hover { color: var(--text); border-color: var(--border-hover); }

  .cl-breadcrumb {
    font-family: var(--font-mono);
    font-size: 0.72rem; color: var(--muted); letter-spacing: 0.06em;
    display: flex; align-items: center; gap: 8px;
  }
  .cl-breadcrumb span { color: var(--green); }

  /* ─── Main layout ─── */
  .cl-main {
    position: relative; z-index: 10;
    flex: 1;
    max-width: 1100px; width: 100%;
    margin: 0 auto;
    padding: 48px 40px 80px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 32px;
    align-items: start;
  }

  /* ─── Section header ─── */
  .cl-header { grid-column: 1 / -1; margin-bottom: 8px; }
  .cl-section-label {
    font-family: var(--font-mono); font-size: 0.72rem;
    letter-spacing: 0.15em; text-transform: uppercase;
    color: var(--green); margin-bottom: 10px;
  }
  .cl-title {
    font-size: 2.2rem; font-weight: 800;
    letter-spacing: -0.02em; line-height: 1.1;
  }
  .cl-subtitle {
    font-family: var(--font-mono); font-size: 0.8rem;
    color: var(--muted); line-height: 1.7; margin-top: 8px;
    max-width: 520px;
  }

  /* ─── Upload panel ─── */
  .cl-upload-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
  }

  .cl-panel-header {
    display: flex; align-items: center; gap: 10px;
    padding: 16px 20px;
    border-bottom: 1px solid var(--border);
    background: rgba(255,255,255,0.02);
  }
  .cl-panel-dot { width: 8px; height: 8px; border-radius: 50%; }
  .cl-panel-dot-g { background: var(--green); box-shadow: 0 0 6px var(--green); }
  .cl-panel-dot-y { background: var(--amber); }
  .cl-panel-dot-r { background: var(--red); }
  .cl-panel-title {
    font-family: var(--font-mono); font-size: 0.7rem;
    letter-spacing: 0.06em; color: var(--muted);
  }

  .cl-panel-body { padding: 24px; }

  /* ─── Drop zone ─── */
  .cl-dropzone {
    border: 2px dashed var(--border);
    border-radius: 12px;
    padding: 40px 24px;
    text-align: center;
    cursor: pointer;
    transition: all 0.25s;
    position: relative;
    background: rgba(74,222,128,0.02);
  }
  .cl-dropzone:hover, .cl-dropzone.drag-over {
    border-color: var(--green);
    background: rgba(74,222,128,0.06);
    box-shadow: 0 0 32px var(--green-glow);
  }
  .cl-dropzone input[type="file"] {
    position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
  }
  .cl-drop-icon { font-size: 2.5rem; margin-bottom: 14px; }
  .cl-drop-title {
    font-size: 0.95rem; font-weight: 700; margin-bottom: 6px;
  }
  .cl-drop-sub {
    font-family: var(--font-mono); font-size: 0.72rem;
    color: var(--muted); line-height: 1.6;
  }
  .cl-drop-sub em { color: var(--green); font-style: normal; }

  /* ─── Preview ─── */
  .cl-preview-wrap {
    margin-top: 20px;
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
    position: relative;
  }
  .cl-preview-bar {
    display: flex; align-items: center; justify-content: space-between;
    padding: 10px 14px;
    background: var(--surface2);
    border-bottom: 1px solid var(--border);
    font-family: var(--font-mono); font-size: 0.68rem; color: var(--muted);
  }
  .cl-preview-badge {
    background: var(--green-glow); color: var(--green);
    padding: 3px 8px; border-radius: 4px;
    font-size: 0.65rem; letter-spacing: 0.08em; text-transform: uppercase;
  }
  .cl-preview-img {
    width: 100%; max-height: 260px;
    object-fit: cover; display: block;
  }
  .cl-preview-remove {
    position: absolute; top: 42px; right: 10px;
    background: rgba(248,113,113,0.15); color: var(--red);
    border: 1px solid rgba(248,113,113,0.3);
    border-radius: 6px; padding: 5px 10px;
    font-family: var(--font-mono); font-size: 0.65rem;
    cursor: pointer; transition: all 0.2s;
  }
  .cl-preview-remove:hover { background: rgba(248,113,113,0.25); }

  /* ─── Predict button ─── */
  .cl-predict-btn {
    width: 100%; margin-top: 20px;
    padding: 14px;
    background: var(--green); color: var(--bg);
    font-family: var(--font-mono); font-size: 0.82rem;
    font-weight: 500; letter-spacing: 0.08em; text-transform: uppercase;
    border: none; border-radius: 10px; cursor: pointer;
    transition: all 0.25s;
    box-shadow: 0 0 24px var(--green-glow);
    display: flex; align-items: center; justify-content: center; gap: 8px;
  }
  .cl-predict-btn:hover:not(:disabled) {
    transform: translateY(-2px);
    box-shadow: 0 0 40px rgba(74,222,128,0.35);
  }
  .cl-predict-btn:disabled {
    opacity: 0.4; cursor: not-allowed; transform: none; box-shadow: none;
  }

  /* ─── Loading bar ─── */
  .cl-loading-bar {
    height: 2px; border-radius: 999px;
    background: var(--border);
    margin-top: 14px; overflow: hidden;
  }
  .cl-loading-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--green), var(--blue));
    animation: loadSweep 1.4s ease-in-out infinite;
    transform-origin: left;
  }
  @keyframes loadSweep {
    0%   { transform: scaleX(0) translateX(0); }
    50%  { transform: scaleX(0.6) translateX(30%); }
    100% { transform: scaleX(0) translateX(200%); }
  }

  /* ─── Info chips below upload ─── */
  .cl-info-chips {
    display: flex; gap: 8px; flex-wrap: wrap;
    margin-top: 16px;
  }
  .cl-info-chip {
    font-family: var(--font-mono); font-size: 0.65rem;
    letter-spacing: 0.06em; text-transform: uppercase;
    color: var(--muted); border: 1px solid var(--border);
    border-radius: 5px; padding: 5px 10px;
  }

  /* ─── Results panel ─── */
  .cl-results-panel {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 16px;
    overflow: hidden;
    animation: fadeUp 0.4s ease both;
  }
  @keyframes fadeUp {
    from { opacity: 0; transform: translateY(16px); }
    to   { opacity: 1; transform: translateY(0); }
  }

  .cl-results-empty {
    padding: 60px 24px;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    text-align: center; gap: 12px;
    color: var(--muted);
    font-family: var(--font-mono); font-size: 0.78rem;
    line-height: 1.7;
    min-height: 300px;
  }
  .cl-results-empty-icon { font-size: 2.5rem; opacity: 0.4; }

  /* Results content */
  .cl-results-body { padding: 24px; }

  .cl-result-class {
    display: flex; align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 20px; gap: 12px;
  }
  .cl-result-class-name {
    font-size: 1.6rem; font-weight: 800;
    letter-spacing: -0.02em; line-height: 1;
  }
  .cl-result-conf-badge {
    font-family: var(--font-mono); font-size: 0.75rem;
    font-weight: 500; letter-spacing: 0.06em;
    background: var(--green-glow); color: var(--green);
    border: 1px solid rgba(74,222,128,0.3);
    padding: 6px 12px; border-radius: 8px;
    white-space: nowrap;
  }

  /* Probability bars */
  .cl-prob-list { display: flex; flex-direction: column; gap: 10px; margin-top: 20px; }
  .cl-prob-row { display: flex; flex-direction: column; gap: 5px; }
  .cl-prob-meta {
    display: flex; justify-content: space-between;
    font-family: var(--font-mono); font-size: 0.7rem;
  }
  .cl-prob-label { color: var(--text); }
  .cl-prob-val { color: var(--muted); }
  .cl-bar-track {
    height: 5px; border-radius: 999px;
    background: rgba(255,255,255,0.05);
  }
  .cl-bar-fill {
    height: 100%; border-radius: 999px;
    background: linear-gradient(90deg, var(--green-dim), var(--green));
    transition: width 0.8s cubic-bezier(0.23,1,0.32,1);
  }
  .cl-bar-fill.top { background: linear-gradient(90deg, var(--green), #86efac); box-shadow: 0 0 8px var(--green-glow); }

  /* Metadata table */
  .cl-meta-table {
    margin-top: 20px;
    border: 1px solid var(--border); border-radius: 10px; overflow: hidden;
  }
  .cl-meta-row {
    display: flex; justify-content: space-between; align-items: center;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    font-family: var(--font-mono); font-size: 0.72rem;
  }
  .cl-meta-row:last-child { border-bottom: none; }
  .cl-meta-key { color: var(--muted); }
  .cl-meta-val { color: var(--text); }

  /* Error state */
  .cl-error {
    margin-top: 14px;
    padding: 12px 16px;
    background: rgba(248,113,113,0.08);
    border: 1px solid rgba(248,113,113,0.25);
    border-radius: 8px;
    font-family: var(--font-mono); font-size: 0.75rem;
    color: var(--red); display: flex; gap: 8px; align-items: flex-start;
  }

  @media (max-width: 800px) {
    .cl-main { grid-template-columns: 1fr; padding: 32px 20px 60px; }
    .cl-header { grid-column: 1; }
    .cl-nav { padding: 14px 20px; }
    .cl-breadcrumb { display: none; }
  }
`;

// ─── EuroSAT class labels (matches your model's output order) ─────────────────
const CLASS_LABELS = [
  "Annual Crop", "Forest", "Herbaceous Vegetation",
  "Highway", "Industrial", "Pasture",
  "Permanent Crop", "Residential", "River", "Sea / Lake",
];

// ─── Sub-components ───────────────────────────────────────────────────────────

function ProbabilityBars({ probabilities, topClass }) {
  if (!probabilities) return null;

  // Convert array or object to sorted pairs
  const pairs = Array.isArray(probabilities)
    ? probabilities.map((p, i) => [CLASS_LABELS[i] ?? `Class ${i}`, p])
    : Object.entries(probabilities);

  const sorted = [...pairs].sort((a, b) => b[1] - a[1]).slice(0, 6);

  return (
    <div className="cl-prob-list">
      {sorted.map(([label, prob]) => {
        const pct = Math.round((prob <= 1 ? prob * 100 : prob) * 10) / 10;
        const isTop = label === topClass;
        return (
          <div className="cl-prob-row" key={label}>
            <div className="cl-prob-meta">
              <span className="cl-prob-label">{label}</span>
              <span className="cl-prob-val">{pct.toFixed(1)}%</span>
            </div>
            <div className="cl-bar-track">
              <div
                className={`cl-bar-fill${isTop ? " top" : ""}`}
                style={{ width: `${pct}%` }}
              />
            </div>
          </div>
        );
      })}
    </div>
  );
}

function ResultsPanel({ prediction, loading }) {
  return (
    <div className="cl-results-panel">
      <div className="cl-panel-header">
        <div className="cl-panel-dot cl-panel-dot-g" />
        <div className="cl-panel-dot cl-panel-dot-y" />
        <div className="cl-panel-dot cl-panel-dot-r" />
        <div className="cl-panel-title">inference · output</div>
      </div>

      {!prediction && !loading && (
        <div className="cl-results-empty">
          <div className="cl-results-empty-icon">🛰️</div>
          <div>
            Upload a satellite image patch<br />
            and run inference to see results
          </div>
        </div>
      )}

      {loading && (
        <div className="cl-results-empty">
          <div className="cl-results-empty-icon">⚙️</div>
          <div>Running ViT inference…<br />Classifying land cover patches</div>
        </div>
      )}

      {prediction && !loading && (
        <div className="cl-results-body">
          {/* Top prediction */}
          <div style={{ marginBottom: 8 }}>
            <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.68rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--muted)", marginBottom: 12 }}>
              // predicted class
            </div>
            <div className="cl-result-class">
              <div className="cl-result-class-name">
                {prediction.predicted_class ?? prediction.class ?? prediction.label ?? "Unknown"}
              </div>
              {(prediction.confidence ?? prediction.probability) != null && (
                <div className="cl-result-conf-badge">
                  {(((prediction.confidence ?? prediction.probability) * 100) || 0).toFixed(1)}% confidence
                </div>
              )}
            </div>
          </div>

          {/* Probability distribution */}
          {(prediction.probabilities ?? prediction.scores ?? prediction.all_classes) && (
            <>
              <div style={{ fontFamily: "var(--font-mono)", fontSize: "0.68rem", letterSpacing: "0.1em", textTransform: "uppercase", color: "var(--muted)", marginBottom: 12 }}>
                // class distribution
              </div>
              <ProbabilityBars
                probabilities={prediction.probabilities ?? prediction.scores ?? prediction.all_classes}
                topClass={prediction.predicted_class ?? prediction.class ?? prediction.label}
              />
            </>
          )}

          {/* Metadata */}
          <div className="cl-meta-table" style={{ marginTop: 24 }}>
            {prediction.model && (
              <div className="cl-meta-row">
                <span className="cl-meta-key">Model</span>
                <span className="cl-meta-val">{prediction.model}</span>
              </div>
            )}
            {prediction.inference_time && (
              <div className="cl-meta-row">
                <span className="cl-meta-key">Inference time</span>
                <span className="cl-meta-val">{prediction.inference_time}</span>
              </div>
            )}
            <div className="cl-meta-row">
              <span className="cl-meta-key">Dataset</span>
              <span className="cl-meta-val">EuroSAT · Sentinel-2</span>
            </div>
            <div className="cl-meta-row">
              <span className="cl-meta-key">Architecture</span>
              <span className="cl-meta-val">Vision Transformer (ViT)</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

// ─── Main component ───────────────────────────────────────────────────────────
const ImageUploader = ({ onPrediction, prediction, onGoHome }) => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [preview, setPreview] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef(null);

  const handleFile = (file) => {
    if (!file) return;
    setSelectedImage(file);
    setPreview(URL.createObjectURL(file));
    setError(null);
    onPrediction(null); // clear previous result
  };

  const handleImageChange = (e) => handleFile(e.target.files[0]);

  const handleDrop = (e) => {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith("image/")) handleFile(file);
  };

  const handleRemove = () => {
    setSelectedImage(null);
    setPreview(null);
    onPrediction(null);
    setError(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const handlePredict = async () => {
    if (!selectedImage) return;
    const formData = new FormData();
    formData.append("image", selectedImage);

    try {
      setLoading(true);
      setError(null);
      const response = await axios.post(
        "http://localhost:8000/predict",
        formData,
        { headers: { "Content-Type": "multipart/form-data" } }
      );
      onPrediction(response.data);
    } catch (err) {
      console.error("Prediction error:", err);
      setError(
        err?.response?.data?.detail ??
        err?.message ??
        "Could not reach the inference server."
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <style>{style}</style>
      <div className="cl-root">
        <div className="cl-grid-bg" />
        <div className="cl-glow" />

        {/* NAV */}
        <nav className="cl-nav">
          <div className="cl-nav-logo" onClick={onGoHome}>
            <div className="cl-logo-icon">🌍</div>
            GeoSentinel
          </div>
          <div className="cl-breadcrumb">
            <span style={{ color: "var(--muted)" }}>Platform</span>
            <span style={{ color: "var(--muted)" }}>›</span>
            <span>Land Cover Classifier</span>
          </div>
          <button className="cl-nav-back" onClick={onGoHome}>
            ← Back to Home
          </button>
        </nav>

        {/* MAIN */}
        <main className="cl-main">
          {/* Header */}
          <div className="cl-header">
            <div className="cl-section-label">// land cover classification</div>
            <h1 className="cl-title">EuroSAT Classifier</h1>
            <p className="cl-subtitle">
              Upload a Sentinel-2 satellite image patch to classify land cover type using our Vision Transformer model trained on the EuroSAT dataset.
            </p>
          </div>

          {/* Upload panel */}
          <div className="cl-upload-panel">
            <div className="cl-panel-header">
              <div className="cl-panel-dot cl-panel-dot-r" />
              <div className="cl-panel-dot cl-panel-dot-y" />
              <div className="cl-panel-dot cl-panel-dot-g" />
              <div className="cl-panel-title">image · input</div>
            </div>
            <div className="cl-panel-body">
              {/* Drop zone */}
              <div
                className={`cl-dropzone${dragOver ? " drag-over" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
              >
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  onChange={handleImageChange}
                />
                <div className="cl-drop-icon">🛰️</div>
                <div className="cl-drop-title">Drop satellite image here</div>
                <div className="cl-drop-sub">
                  or <em>click to browse</em> your files<br />
                  PNG, JPG, TIF · Sentinel-2 patches recommended
                </div>
              </div>

              {/* Preview */}
              {preview && (
                <div className="cl-preview-wrap">
                  <div className="cl-preview-bar">
                    <span>{selectedImage?.name ?? "image"}</span>
                    <span className="cl-preview-badge">Ready</span>
                  </div>
                  <img src={preview} alt="preview" className="cl-preview-img" />
                  <button className="cl-preview-remove" onClick={handleRemove}>✕ Remove</button>
                </div>
              )}

              {/* Error */}
              {error && (
                <div className="cl-error">
                  <span>⚠</span>
                  <span>{error}</span>
                </div>
              )}

              {/* Loading bar */}
              {loading && (
                <div className="cl-loading-bar">
                  <div className="cl-loading-fill" />
                </div>
              )}

              {/* Predict button */}
              <button
                className="cl-predict-btn"
                onClick={handlePredict}
                disabled={!selectedImage || loading}
              >
                {loading ? (
                  <>⚙ &nbsp;Running Inference…</>
                ) : (
                  <>⚡ &nbsp;Classify Land Cover</>
                )}
              </button>

              {/* Info chips */}
              <div className="cl-info-chips">
                <span className="cl-info-chip">ViT-B/16</span>
                <span className="cl-info-chip">EuroSAT</span>
                <span className="cl-info-chip">10 Classes</span>
                <span className="cl-info-chip">64×64px</span>
                <span className="cl-info-chip">Sentinel-2</span>
              </div>
            </div>
          </div>

          {/* Results panel */}
          <ResultsPanel prediction={prediction} loading={loading} />
        </main>
      </div>
    </>
  );
};

export default ImageUploader;
