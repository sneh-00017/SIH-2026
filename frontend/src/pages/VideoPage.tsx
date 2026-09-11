import { useState } from "react";
import type { ChangeEvent, FormEvent } from "react";
import Sidebar from "../components/Sidebar";
import { API_BASE_URL } from "../api/client";

type FramePoint = { frame_number: number; risk_score: number; motion_score: number; status: "danger" | "person" | "clear"; has_person: boolean };
type EvidenceFrame = { frame_number: number; status: "danger" | "person" | "clear"; risk_score: number; motion_score: number; image: string };
type VideoResult = { risk_score?: number; score?: number; risk_level?: string; hazards?: string[]; explanation?: string[]; risk_factors?: Array<{ label: string; percentage: number }>; detected_objects?: Array<Record<string, unknown>>; sampled_frames?: number; video_frames?: number; disclaimer?: string; evidence_frame?: string | null; frame_status?: string; motion_score?: number; frame_number?: number; frame_timeline?: FramePoint[]; evidence_frames?: EvidenceFrame[]; output_video_url?: string; output_video_filename?: string };

export default function VideoPage() {
  const [file, setFile] = useState<File | null>(null);
  const [videoPreview, setVideoPreview] = useState<string | null>(null);
  const [result, setResult] = useState<VideoResult | null>(null);
  const [selectedEvidence, setSelectedEvidence] = useState<EvidenceFrame | null>(null);
  const [busy, setBusy] = useState(false);
  const [message, setMessage] = useState("Choose an MP4, MOV, or AVI video to begin.");

  const handleFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const nextFile = event.target.files?.[0] ?? null;
    setFile(nextFile);
    if (videoPreview) URL.revokeObjectURL(videoPreview);
    setVideoPreview(nextFile ? URL.createObjectURL(nextFile) : null);
    setResult(null);
    setSelectedEvidence(null);
  };

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setMessage("Select a video before starting detection.");
      return;
    }
    setBusy(true);
    setMessage("Sampling frames at 2 FPS and checking movement, people, and hazards...");
    try {
      const body = new FormData();
      body.append("video", file);
      const response = await fetch(`${API_BASE_URL}/analyze-video`, { method: "POST", body });
      const data = (await response.json()) as VideoResult & { error?: string };
      if (!response.ok) throw new Error(data.error ?? "Video analysis failed.");
      setResult(data);
      setSelectedEvidence(data.evidence_frames?.[0] ?? null);
      setMessage(`Video analysis complete · ${data.sampled_frames ?? 0} frames checked`);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Video analysis failed.");
    } finally {
      setBusy(false);
    }
  };

  const score = result?.risk_score ?? result?.score ?? 0;
  const activeEvidence = selectedEvidence ?? (result?.evidence_frame ? {
    frame_number: result.frame_number ?? 0,
    status: (result.frame_status ?? "clear") as EvidenceFrame["status"],
    risk_score: score,
    motion_score: result.motion_score ?? 0,
    image: result.evidence_frame,
  } : null);

  return (
    <div className="app-shell"><Sidebar /><main className="dashboard-card">
      <header className="page-heading"><div><span className="eyebrow">Frame sampling</span><h1>Video detection</h1><p>Review movement across sampled frames and identify the highest observed safety risk.</p></div><span className={`status-pill ${result ? "success" : ""}`}>{result ? "Analysis ready" : "Video workflow"}</span></header>
      <form className="video-upload panel" onSubmit={handleSubmit}><label className="video-drop"><input type="file" accept="video/mp4,video/quicktime,video/x-msvideo" onChange={handleFileChange} /><span className="video-icon">▶</span><strong>{file ? file.name : "Choose a workplace video"}</strong><small>Detection samples 2 frames per second and filters detections below 35% confidence.</small></label>{videoPreview && <div className="video-stage"><video src={videoPreview} controls muted /><div className={`scan-overlay ${busy ? "active" : ""}`}><span>{busy ? "Scanning movement and hazards..." : "Video ready"}</span><i /></div></div>}<div className="video-actions"><span>{message}</span><button className="submit-btn" type="submit" disabled={!file || busy}>{busy ? "Scanning frames..." : "Analyze video"}</button></div></form>
      {result && <section className="results-panel panel"><div className="result-header"><div><span className="card-label">Full annotated output</span><h3>{result.risk_level ?? "LOW"} risk detected</h3></div><div className="score-badge">{score}%</div></div>{result.output_video_url && <div className="output-video-wrap"><video src={`${API_BASE_URL}${result.output_video_url}`} controls playsInline /><a className="outline-btn" href={`${API_BASE_URL}${result.output_video_url}`} download={result.output_video_filename ?? "safesight-analysis.webm"}>Download annotated video</a></div>}
        <div className="evidence-layout"><div><div className={`evidence-frame large ${activeEvidence?.status ?? "clear"}`}>{activeEvidence?.image ? <img src={activeEvidence.image} alt="Annotated video detection frame" /> : <span>No evidence frame returned</span>}</div><div className="evidence-caption"><span>Frame {activeEvidence?.frame_number ?? 0}</span><span>{activeEvidence?.motion_score ?? 0}% motion</span><span>{activeEvidence?.status ?? "clear"}</span></div></div><div className="evidence-legend"><h4>Detection colors</h4><p><i className="legend-swatch danger" />Red: active danger or significant movement</p><p><i className="legend-swatch person" />Green: person detected without active danger</p><p><i className="legend-swatch clear" />Gray: no person or hazard detected</p></div></div>
        <div className="evidence-gallery">{(result.evidence_frames ?? []).map((frame) => <button type="button" className={`evidence-thumb ${frame.status} ${activeEvidence?.frame_number === frame.frame_number ? "selected" : ""}`} key={frame.frame_number} onClick={() => setSelectedEvidence(frame)}><img src={frame.image} alt={`Frame ${frame.frame_number}`} /><span>#{frame.frame_number} · {frame.status}</span></button>)}</div>
        <div className="risk-meta"><div><span>Frames sampled</span><strong>{result.sampled_frames ?? 0}</strong></div><div><span>Video frames</span><strong>{result.video_frames ?? 0}</strong></div><div><span>Hazards</span><strong>{result.hazards?.length ?? 0}</strong></div><div><span>Objects</span><strong>{result.detected_objects?.length ?? 0}</strong></div></div>
        <div className="frame-timeline"><h4>Frame detection timeline</h4><div>{(result.frame_timeline ?? []).map((frame) => <span className={`timeline-frame ${frame.status}`} title={`Frame ${frame.frame_number}: ${frame.status}, ${frame.motion_score}% motion`} key={frame.frame_number} />)}</div></div>
        <div className="result-grid"><div className="result-card"><h4>Risk contribution</h4><div className="factor-list">{(result.risk_factors ?? []).map((factor) => <div className="factor" key={factor.label}><div><span>{factor.label}</span><strong>{factor.percentage}%</strong></div><div className="factor-track"><i style={{ width: `${factor.percentage}%` }} /></div></div>)}</div></div><div className="result-card"><h4>Detection explanation</h4><p className="result-copy">{(result.explanation ?? []).join(" ") || "No active hazards were detected."}</p><p className="result-copy">{(result.hazards ?? []).join(" · ") || "Clear frame"}</p></div></div>
        {result.disclaimer && <p className="disclaimer">{result.disclaimer}</p>}
      </section>}
    </main></div>
  );
}
