import { useEffect, useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import Sidebar from "../components/Sidebar";
import { checkBackendHealth } from "../api/health";
import { API_BASE_URL } from "../api/client";

type RiskResult = {
  risk_score?: number;
  score?: number;
  risk_level?: string;
  hazards?: string[];
  explanation?: string[];
  risk_factors?: Array<{ label: string; percentage: number; weight: number }>;
  disclaimer?: string;
  detected_objects?: Array<Record<string, unknown>>;
  person_detected?: boolean;
  vehicle_detected?: boolean;
  person_near_vehicle?: boolean;
};

export default function HomePage() {
  const [message, setMessage] = useState("System online and ready for inspection");
  const [status, setStatus] = useState<"idle" | "checking" | "success" | "error">(
    "checking",
  );
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [result, setResult] = useState<RiskResult | null>(null);
  const [isUploading, setIsUploading] = useState(false);

  useEffect(() => {
    let ignore = false;

    const verifySystem = async () => {
      const backendStatus = await checkBackendHealth();
      if (ignore) return;

      const online = backendStatus.includes("✅");
      setStatus(online ? "success" : "error");
      setMessage(
        online ? "System online and ready for inspection" : "Backend unavailable",
      );
    };

    void verifySystem();
    return () => {
      ignore = true;
    };
  }, []);

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0] ?? null;
    setSelectedFile(file);

    if (file) {
      const objectUrl = URL.createObjectURL(file);
      setPreviewUrl((current) => {
        if (current) URL.revokeObjectURL(current);
        return objectUrl;
      });
    } else {
      setPreviewUrl(null);
    }
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    if (!selectedFile) {
      setStatus("error");
      setMessage("Please choose an image first.");
      return;
    }

    setIsUploading(true);
    setStatus("checking");
    setMessage("Analyzing image for hazards...");

    try {
      const formData = new FormData();
      formData.append("image", selectedFile);

      const response = await fetch(`${API_BASE_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(errorText || `HTTP ${response.status}`);
      }

      const data = (await response.json()) as RiskResult & {
        risk_assessment?: RiskResult;
      };

      const riskAssessment = data.risk_assessment ?? data;
      setResult(riskAssessment);
      setStatus("success");
      setMessage(
        `Risk analysis complete: ${riskAssessment.risk_level ?? "LOW"} risk`,
      );
    } catch (error) {
      console.error(error);
      setStatus("error");
      setMessage(
        "Unable to analyze the image. Please check the backend and try again.",
      );
    } finally {
      setIsUploading(false);
    }
  };

  const score = result?.risk_score ?? result?.score ?? 18;
  const level = result?.risk_level ?? "LOW";
  const riskFactors = result?.risk_factors ?? [];

  return (
    <div className="app-shell"><Sidebar /><main className="dashboard-card">
        <header className="topbar">
          <div>
            <span className="eyebrow">Safety intelligence</span>
            <h2>Image analysis</h2>
          </div>
          <div className="topbar-right">
            <div className={`status-pill ${status}`}>
              {status === "checking"
                ? "Checking"
                : status === "success"
                  ? "System online"
                  : status === "error"
                    ? "Offline"
                    : "Standby"}
            </div>
            <small className="status-message">{message}</small>
          </div>
        </header>

        <section className="hero">
          <div className="hero-copy">
            <span className="kicker">Active monitoring</span>
            <h1>AI Serious Injury / Fatality Risk Detector</h1>
            <p>
              Detect unsafe work conditions, PPE violations, and proximity risks with
              AI-based site assessment in seconds.
            </p>
          </div>

          <div className="hero-stat">
            <small>Current risk score</small>
            <strong>{score}%</strong>
            <span>{level}</span>
          </div>
        </section>

        <section className="overview-grid">
          <div className="metric-card accent">
            <span>Detections</span>
            <strong>{result ? (result.detected_objects?.length ?? 0) : 12}</strong>
            <small>Objects identified</small>
          </div>
          <div className="metric-card">
            <span>Incidents</span>
            <strong>{result ? (result.hazards?.length ?? 0) : 3}</strong>
            <small>Open hazards</small>
          </div>
          <div className="metric-card">
            <span>Compliance</span>
            <strong>{result ? (result.risk_level === "LOW" ? "87%" : "64%") : "87%"}</strong>
            <small>PPE compliance</small>
          </div>
          <div className="metric-card">
            <span>Zone status</span>
            <strong>{result ? (level === "HIGH" ? "Alert" : "Stable") : "Stable"}</strong>
            <small>Activity state</small>
          </div>
        </section>

        <section className="content-grid">
          <form className="panel upload-panel" onSubmit={handleSubmit}>
            <div className="panel-header">
              <div>
                <span className="card-label">Upload image</span>
                <h3>Run AI risk assessment</h3>
              </div>
            </div>

            <label className="file-picker">
              <input type="file" accept="image/*" onChange={handleFileChange} />
              <span>{selectedFile ? selectedFile.name : "Choose a safety image"}</span>
            </label>

            {previewUrl ? (
              <div className="preview-box">
                <img src={previewUrl} alt="Selected preview" />
              </div>
            ) : (
              <div className="empty-preview">
                <span>No image selected</span>
              </div>
            )}

            <button className="submit-btn" type="submit" disabled={!selectedFile || isUploading}>
              {isUploading ? "Analyzing..." : "Analyze Risk"}
            </button>
          </form>

          <div className="panel analysis-guide"><span className="card-label">Inspection mode</span><h3>Explainable results</h3><p>Every assessment returns a risk percentage, detected hazards, and a contribution breakdown tied to the safety model.</p><span className="guide-value">No opaque black-box verdicts</span></div>
        </section>

        {result ? (
          <section className="results-panel panel">
            <div className="result-header">
              <div>
                <span className="card-label">Assessment result</span>
                <h3>Live analysis</h3>
              </div>
              <div className="score-badge">{score}%</div>
            </div>

            <div className="risk-meta">
              <div>
                <span>Risk level</span>
                <strong>{level}</strong>
              </div>
              <div>
                <span>Person</span>
                <strong>{result.person_detected ? "Yes" : "No"}</strong>
              </div>
              <div>
                <span>Vehicle</span>
                <strong>{result.vehicle_detected ? "Yes" : "No"}</strong>
              </div>
              <div>
                <span>Near vehicle</span>
                <strong>{result.person_near_vehicle ? "Yes" : "No"}</strong>
              </div>
            </div>

            <div className="result-grid">
              <div className="result-card">
                <h4>Hazards</h4>
                <ul>
                  {(result.hazards ?? []).length > 0 ? (
                    (result.hazards ?? []).map((item, index) => <li key={index}>{item}</li>)
                  ) : (
                    <li>No hazards detected.</li>
                  )}
                </ul>
              </div>

              <div className="result-card">
                <h4>Why this score</h4>
                <p className="result-copy">Each factor contributes to the overall score shown above. These percentages add up to the total heuristic risk percentage.</p>
                <div className="factor-list">
                  {riskFactors.length > 0 ? riskFactors.map((factor) => (
                    <div className="factor" key={factor.label}><div><span>{factor.label}</span><strong>{factor.percentage}%</strong></div><div className="factor-track"><i style={{ width: `${factor.percentage}%` }} /></div></div>
                  )) : <span className="clear-state">No active risk factors detected · 0%</span>}
                </div>
              </div>
            </div>

            <div className="explanation-line">{(result.explanation ?? []).length > 0 ? result.explanation?.join(" ") : "Assessment is currently clear."}</div>

            {result.detected_objects && result.detected_objects.length > 0 ? (
              <div className="result-card full-width">
                <h4>Detected objects</h4>
                <ul className="object-list">
                  {result.detected_objects.map((item, index) => {
                    const name = (item.class_name ?? item.class ?? "Unknown") as string;
                    const confidence = item.confidence ? ` (${item.confidence})` : "";
                    return <li key={index}>{name}{confidence}</li>;
                  })}
                </ul>
              </div>
            ) : null}

            {result.disclaimer ? <p className="disclaimer">{result.disclaimer}</p> : null}
          </section>
        ) : null}
      </main>
    </div>
  );
}