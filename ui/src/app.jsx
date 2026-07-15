import { useState, useRef, useCallback } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const SEVERITY_CONFIG = {
  none:     { color: "#0ea472", bg: "rgba(14,164,114,0.08)", label: "HEALTHY",  icon: "●" },
  moderate: { color: "#e8941a", bg: "rgba(232,148,26,0.08)", label: "MODERATE", icon: "▲" },
  high:     { color: "#d93b3b", bg: "rgba(217,59,59,0.08)",  label: "HIGH",     icon: "■" },
  critical: { color: "#9b2de0", bg: "rgba(155,45,224,0.08)", label: "CRITICAL", icon: "◆" },
  unknown:  { color: "#6b7280", bg: "rgba(107,114,128,0.08)", label: "UNKNOWN", icon: "?" },
};

const css = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&family=Playfair+Display:wght@500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: #f4f3f0; font-family: 'DM Sans', sans-serif; color: #1a1a1a; }

  .app { min-height: 100vh; display: grid; grid-template-rows: auto 1fr; }

  /* Header */
  .header {
    background: #0f1923;
    padding: 0 48px;
    height: 64px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 100;
  }
  .header-logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }
  .header-mark {
    width: 32px; height: 32px;
    background: #0ea472;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px;
  }
  .header-title {
    font-family: 'Playfair Display', serif;
    font-size: 17px;
    font-weight: 600;
    color: #fff;
    letter-spacing: 0.01em;
  }
  .header-sub {
    font-size: 11px;
    color: #4a6070;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
    text-transform: uppercase;
  }
  .header-status {
    display: flex;
    align-items: center;
    gap: 6px;
    font-size: 11px;
    color: #4a6070;
    font-family: 'DM Mono', monospace;
  }
  .status-dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #0ea472;
    animation: pulse 2s ease-in-out infinite;
  }
  @keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
  }

  /* Main layout */
  .main {
    display: grid;
    grid-template-columns: 1fr 1fr;
    min-height: calc(100vh - 64px);
  }

  /* Left panel */
  .left-panel {
    background: #fff;
    border-right: 1px solid #e8e5e0;
    display: flex;
    flex-direction: column;
    padding: 48px;
  }
  .panel-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 24px;
  }
  .section-title {
    font-family: 'Playfair Display', serif;
    font-size: 26px;
    font-weight: 500;
    color: #0f1923;
    line-height: 1.3;
    margin-bottom: 10px;
  }
  .section-desc {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.7;
    margin-bottom: 40px;
  }

  /* Upload zone */
  .upload-zone {
    flex: 1;
    border: 1.5px dashed #d1cdc7;
    border-radius: 4px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all 0.2s;
    background: #fafaf9;
    min-height: 260px;
    position: relative;
    overflow: hidden;
  }
  .upload-zone:hover, .upload-zone.drag-over {
    border-color: #0ea472;
    background: rgba(14,164,114,0.03);
  }
  .upload-icon {
    width: 52px; height: 52px;
    border: 1.5px solid #d1cdc7;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    margin-bottom: 16px;
    color: #9ca3af;
    background: #fff;
  }
  .upload-primary {
    font-size: 14px;
    font-weight: 500;
    color: #374151;
    margin-bottom: 6px;
  }
  .upload-secondary {
    font-size: 12px;
    color: #9ca3af;
    font-family: 'DM Mono', monospace;
  }

  /* Image preview */
  .preview-wrap {
    flex: 1;
    position: relative;
    border-radius: 4px;
    overflow: hidden;
    min-height: 260px;
    background: #0f1923;
  }
  .preview-img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    opacity: 0.92;
  }
  .preview-overlay {
    position: absolute;
    inset: 0;
    background: linear-gradient(to top, rgba(15,25,35,0.7) 0%, transparent 50%);
  }
  .preview-actions {
    position: absolute;
    bottom: 16px; left: 16px; right: 16px;
    display: flex;
    gap: 10px;
  }
  .btn-analyze {
    flex: 1;
    padding: 12px 20px;
    background: #0ea472;
    color: #fff;
    border: none;
    border-radius: 3px;
    font-size: 13px;
    font-weight: 600;
    font-family: 'DM Sans', sans-serif;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    cursor: pointer;
    transition: background 0.15s;
    display: flex; align-items: center; justify-content: center; gap: 8px;
  }
  .btn-analyze:hover { background: #0b8f62; }
  .btn-analyze:disabled { background: #4a6070; cursor: not-allowed; }
  .btn-clear {
    padding: 12px 16px;
    background: rgba(255,255,255,0.1);
    color: #fff;
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 3px;
    font-size: 12px;
    cursor: pointer;
    font-family: 'DM Sans', sans-serif;
    transition: background 0.15s;
  }
  .btn-clear:hover { background: rgba(255,255,255,0.2); }

  /* Right panel */
  .right-panel {
    background: #f4f3f0;
    padding: 48px;
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  /* Result card */
  .result-card {
    background: #fff;
    border-radius: 4px;
    border: 1px solid #e8e5e0;
    overflow: hidden;
  }
  .result-header {
    padding: 20px 24px;
    border-bottom: 1px solid #f0ede8;
    display: flex;
    align-items: center;
    justify-content: space-between;
  }
  .result-plant {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 4px;
  }
  .result-name {
    font-family: 'Playfair Display', serif;
    font-size: 20px;
    font-weight: 500;
    color: #0f1923;
  }
  .severity-badge {
    padding: 5px 12px;
    border-radius: 2px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
  }

  /* Confidence meter */
  .confidence-wrap {
    padding: 16px 24px;
    border-bottom: 1px solid #f0ede8;
  }
  .confidence-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
  }
  .confidence-label {
    font-size: 11px;
    color: #9ca3af;
    font-family: 'DM Mono', monospace;
    text-transform: uppercase;
    letter-spacing: 0.08em;
  }
  .confidence-value {
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    font-weight: 500;
  }
  .meter-track {
    height: 3px;
    background: #f0ede8;
    border-radius: 0;
    overflow: hidden;
  }
  .meter-fill {
    height: 100%;
    border-radius: 0;
    transition: width 1s cubic-bezier(0.4, 0, 0.2, 1);
  }

  /* Info rows */
  .info-body {
    padding: 20px 24px;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .info-row {
    display: grid;
    grid-template-columns: 90px 1fr;
    gap: 12px;
    align-items: flex-start;
  }
  .info-key {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9ca3af;
    padding-top: 2px;
  }
  .info-val {
    font-size: 13px;
    color: #374151;
    line-height: 1.6;
  }

  /* Healthy state */
  .healthy-body {
    padding: 28px 24px;
    display: flex;
    align-items: center;
    gap: 16px;
  }
  .healthy-icon {
    width: 44px; height: 44px;
    border-radius: 50%;
    background: rgba(14,164,114,0.1);
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    flex-shrink: 0;
  }
  .healthy-text { font-size: 13px; color: #374151; line-height: 1.6; }
  .healthy-title { font-weight: 600; color: #0ea472; margin-bottom: 3px; }

  /* Alternatives */
  .alt-card {
    background: #fff;
    border: 1px solid #e8e5e0;
    border-radius: 4px;
    overflow: hidden;
  }
  .alt-header {
    padding: 14px 20px;
    border-bottom: 1px solid #f0ede8;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9ca3af;
  }
  .alt-row {
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    border-bottom: 1px solid #f9f8f6;
  }
  .alt-row:last-child { border-bottom: none; }
  .alt-name { font-size: 13px; font-weight: 500; color: #374151; }
  .alt-plant { font-size: 11px; color: #9ca3af; margin-top: 1px; }
  .alt-right { display: flex; align-items: center; gap: 10px; }
  .alt-pct {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: #6b7280;
  }

  /* Empty state */
  .empty-state {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .empty-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1px;
    background: #e8e5e0;
    border: 1px solid #e8e5e0;
    border-radius: 4px;
    overflow: hidden;
    margin-bottom: 24px;
  }
  .empty-cell {
    background: #fff;
    padding: 16px 18px;
  }
  .empty-cell-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #9ca3af;
    margin-bottom: 6px;
  }
  .empty-cell-val {
    font-size: 13px;
    color: #374151;
    font-weight: 500;
  }
  .plants-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #9ca3af;
    margin-bottom: 12px;
  }
  .plants-list {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }
  .plant-tag {
    font-size: 12px;
    padding: 5px 12px;
    background: #fff;
    border: 1px solid #e8e5e0;
    border-radius: 2px;
    color: #374151;
    font-family: 'DM Mono', monospace;
  }

  /* Error */
  .error-bar {
    background: #fff;
    border: 1px solid #f5c6c6;
    border-left: 3px solid #d93b3b;
    border-radius: 4px;
    padding: 14px 18px;
    font-size: 13px;
    color: #d93b3b;
    line-height: 1.5;
  }

  /* Loading spinner */
  @keyframes spin { to { transform: rotate(360deg); } }
  .spinner {
    width: 14px; height: 14px;
    border: 2px solid rgba(255,255,255,0.3);
    border-top-color: #fff;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  /* Scan again */
  .btn-scan-again {
    width: 100%;
    padding: 12px;
    background: transparent;
    border: 1px solid #e8e5e0;
    border-radius: 3px;
    font-size: 12px;
    color: #6b7280;
    cursor: pointer;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    transition: all 0.15s;
  }
  .btn-scan-again:hover { border-color: #9ca3af; color: #374151; }

  @media (max-width: 768px) {
    .main { grid-template-columns: 1fr; }
    .left-panel, .right-panel { padding: 28px 20px; }
    .header { padding: 0 20px; }
  }
`;

function SeverityBadge({ severity }) {
  const c = SEVERITY_CONFIG[severity] || SEVERITY_CONFIG.unknown;
  return (
    <span className="severity-badge" style={{ background: c.bg, color: c.color }}>
      {c.icon} {c.label}
    </span>
  );
}

function ResultPanel({ result, onReset }) {
  const top = result.top_prediction;
  const c = SEVERITY_CONFIG[top.severity] || SEVERITY_CONFIG.unknown;

  return (
    <>
      <div className="result-card">
        <div className="result-header">
          <div>
            <div className="result-plant">{top.plant}</div>
            <div className="result-name">{top.name}</div>
          </div>
          <SeverityBadge severity={top.severity} />
        </div>

        <div className="confidence-wrap">
          <div className="confidence-row">
            <span className="confidence-label">Confidence Score</span>
            <span className="confidence-value" style={{ color: c.color }}>{top.confidence}%</span>
          </div>
          <div className="meter-track">
            <div className="meter-fill" style={{ width: `${top.confidence}%`, background: c.color }} />
          </div>
        </div>

        {top.severity === "none" ? (
          <div className="healthy-body">
            <div className="healthy-icon">✓</div>
            <div className="healthy-text">
              <div className="healthy-title">No disease detected</div>
              {top.prevention}
            </div>
          </div>
        ) : (
          <div className="info-body">
            <div className="info-row">
              <span className="info-key">Symptoms</span>
              <span className="info-val">{top.symptoms}</span>
            </div>
            <div className="info-row">
              <span className="info-key">Treatment</span>
              <span className="info-val">{top.treatment}</span>
            </div>
            <div className="info-row">
              <span className="info-key">Prevention</span>
              <span className="info-val">{top.prevention}</span>
            </div>
          </div>
        )}
      </div>

      {result.alternatives?.length > 0 && (
        <div className="alt-card">
          <div className="alt-header">Differential Diagnosis</div>
          {result.alternatives.map((alt, i) => (
            <div className="alt-row" key={i}>
              <div>
                <div className="alt-name">{alt.name}</div>
                <div className="alt-plant">{alt.plant}</div>
              </div>
              <div className="alt-right">
                <SeverityBadge severity={alt.severity} />
                <span className="alt-pct">{alt.confidence}%</span>
              </div>
            </div>
          ))}
        </div>
      )}

      <button className="btn-scan-again" onClick={onReset}>
        ← New Scan
      </button>
    </>
  );
}

function EmptyPanel() {
  return (
    <div className="empty-state">
      <div className="empty-grid">
        {[
          ["Model", "MobileNetV2"],
          ["Dataset", "PlantVillage"],
          ["Classes", "15 diseases"],
          ["Input", "224 × 224 px"],
        ].map(([k, v]) => (
          <div className="empty-cell" key={k}>
            <div className="empty-cell-label">{k}</div>
            <div className="empty-cell-val">{v}</div>
          </div>
        ))}
      </div>

      <div className="plants-label">Supported Crops</div>
      <div className="plants-list">
        {["Bell Pepper", "Potato", "Tomato"].map(p => (
          <span className="plant-tag" key={p}>{p}</span>
        ))}
      </div>
    </div>
  );
}

export default function App() {
  const [dragOver, setDragOver] = useState(false);
  const [image, setImage]       = useState(null);
  const [loading, setLoading]   = useState(false);
  const [result, setResult]     = useState(null);
  const [error, setError]       = useState(null);
  const inputRef = useRef();

  const handleFile = useCallback((file) => {
    if (!file?.type.startsWith("image/")) {
      setError("Please upload a valid image file (JPEG or PNG).");
      return;
    }
    setError(null);
    setResult(null);
    setImage({ url: URL.createObjectURL(file), file });
  }, []);

  const handleDrop = useCallback((e) => {
    e.preventDefault();
    setDragOver(false);
    handleFile(e.dataTransfer.files[0]);
  }, [handleFile]);

  const handleAnalyze = async () => {
    if (!image) return;
    setLoading(true);
    setError(null);
    setResult(null);
    const fd = new FormData();
    fd.append("file", image.file);
    try {
      const res  = await fetch(`${API_URL}/predict`, { method: "POST", body: fd });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Prediction failed.");
      setResult(data);
    } catch (err) {
      setError(err.message.includes("fetch")
        ? "Cannot connect to API. Run: cd api && uvicorn main:app --reload --port 8000"
        : err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setImage(null); setResult(null); setError(null);
    if (inputRef.current) inputRef.current.value = "";
  };

  return (
    <>
      <style>{css}</style>
      <div className="app">
        {/* Header */}
        <header className="header">
          <div className="header-logo">
            <div className="header-mark">🌿</div>
            <div>
              <div className="header-title">LeafScan</div>
            </div>
          </div>
          <div className="header-status">
            <div className="status-dot" />
            DIAGNOSTIC SYSTEM ONLINE
          </div>
          <div className="header-sub">Plant Pathology · Deep Learning</div>
        </header>

        {/* Two-column layout */}
        <div className="main">
          {/* Left — upload */}
          <div className="left-panel">
            <div className="panel-label">01 / Input</div>
            <div className="section-title">Leaf Specimen<br />Analysis</div>
            <p className="section-desc">
              Upload a photograph of a plant leaf for automated disease identification using convolutional neural network analysis.
            </p>

            {!image ? (
              <div
                className={`upload-zone ${dragOver ? "drag-over" : ""}`}
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={handleDrop}
                onClick={() => inputRef.current?.click()}
              >
                <div className="upload-icon">↑</div>
                <div className="upload-primary">Drop leaf image here</div>
                <div className="upload-secondary">JPEG · PNG · max 10MB</div>
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/jpeg,image/png,image/jpg"
                  style={{ display: "none" }}
                  onChange={(e) => handleFile(e.target.files[0])}
                />
              </div>
            ) : (
              <div className="preview-wrap">
                <img src={image.url} alt="Leaf specimen" className="preview-img" />
                <div className="preview-overlay" />
                <div className="preview-actions">
                  <button
                    className="btn-analyze"
                    onClick={handleAnalyze}
                    disabled={loading}
                  >
                    {loading
                      ? <><div className="spinner" /> Analyzing...</>
                      : "Run Analysis"
                    }
                  </button>
                  <button className="btn-clear" onClick={handleReset}>✕</button>
                </div>
              </div>
            )}
          </div>

          {/* Right — results */}
          <div className="right-panel">
            <div className="panel-label">02 / Diagnosis</div>

            {error && <div className="error-bar">⚠ {error}</div>}

            {result
              ? <ResultPanel result={result} onReset={handleReset} />
              : <EmptyPanel />
            }
          </div>
        </div>
      </div>
    </>
  );
}