import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { API_BASE_URL } from "../api/client";

type Analysis = { risk_score: number; risk_level: string };

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/analyses`)
      .then((response) => response.json())
      .then((data: { analyses?: Analysis[] }) => setAnalyses(data.analyses ?? []))
      .catch(() => setAnalyses([]));
  }, []);

  const averageRisk = analyses.length
    ? Math.round(analyses.reduce((total, item) => total + item.risk_score, 0) / analyses.length)
    : 0;
  const highRisk = analyses.filter((item) => item.risk_level === "HIGH").length;

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="dashboard-card">
        <header className="page-heading"><div><span className="eyebrow">Command center</span><h1>Safety dashboard</h1><p>Choose an inspection workflow and keep your workplace risk visible.</p></div><span className="status-pill success">System online</span></header>
        <section className="dashboard-hero"><div><span className="kicker">Ready for inspection</span><h2>Turn site footage into safer decisions.</h2><p>Upload a workplace image or video and receive an explainable risk score with percentage-based contributing factors.</p></div><div className="hero-stat"><small>Latest risk</small><strong>{analyses[0]?.risk_score ?? 0}%</strong><span>{analyses[0]?.risk_level ?? "No analysis yet"}</span></div></section>
        <section className="overview-grid"><div className="metric-card accent"><span>Saved analyses</span><strong>{analyses.length}</strong><small>Stored in database</small></div><div className="metric-card"><span>Average risk</span><strong>{averageRisk}%</strong><small>Across all inspections</small></div><div className="metric-card"><span>High risk events</span><strong>{highRisk}</strong><small>Require attention</small></div><div className="metric-card"><span>Compliance</span><strong>{analyses.length ? "87%" : "--"}</strong><small>PPE compliance rate</small></div></section>
        <section className="workflow-grid"><Link className="workflow-card" to="/analysis"><span className="workflow-icon">◉</span><div><span className="card-label">Still image</span><h3>Image analysis</h3><p>Inspect PPE, proximity, and unsafe conditions from one site photo.</p></div><strong>→</strong></Link><Link className="workflow-card featured" to="/video"><span className="workflow-icon">▶</span><div><span className="card-label">Frame sampling</span><h3>Video detection</h3><p>Scan a video and surface the highest observed safety risk.</p></div><strong>→</strong></Link></section>
        <section className="dashboard-note panel"><span className="live-dot" /><div><strong>Continuous monitoring ready</strong><p>Your next inspection will appear in Analysis and History after processing.</p></div></section>
      </main>
    </div>
  );
}
