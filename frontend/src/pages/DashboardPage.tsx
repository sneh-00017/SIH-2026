import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { API_BASE_URL } from "../api/client";

type Analysis = { risk_score: number; risk_level: string };

export default function DashboardPage() {
  const [analyses, setAnalyses] = useState<Analysis[]>([]);
  const [isRefreshing, setIsRefreshing] = useState(false);

  const refreshDashboard = async () => {
    setIsRefreshing(true);
    try {
      const response = await fetch(`${API_BASE_URL}/api/analyses`);
      if (!response.ok) throw new Error("Dashboard refresh failed");
      const data = (await response.json()) as { analyses?: Analysis[] };
      setAnalyses(data.analyses ?? []);
    } catch {
      setAnalyses([]);
    } finally {
      setIsRefreshing(false);
    }
  };

  useEffect(() => {
    refreshDashboard();
  }, []);

  const averageRisk = analyses.length
    ? Math.round(analyses.reduce((total, item) => total + item.risk_score, 0) / analyses.length)
    : 0;
  const highRisk = analyses.filter((item) => item.risk_level === "HIGH").length;

  return (
    <div className="app-shell">
      <Sidebar />
      <main className="dashboard-card dashboard-page">
        <header className="page-heading"><div><span className="eyebrow">Command center</span><h1>Safety dashboard</h1><p>Choose an inspection workflow and keep your workplace risk visible.</p></div><div className="dashboard-actions"><button className="refresh-btn" type="button" onClick={refreshDashboard} disabled={isRefreshing} title="Refresh dashboard data" aria-label="Refresh dashboard data">{isRefreshing ? "..." : "↻"}</button><span className="status-pill success">System online</span></div></header>
        <section className="dashboard-hero"><div className="dashboard-hero-copy"><span className="kicker">Ready for inspection</span><h2>Turn site footage into safer decisions.</h2><p>Upload a workplace image or video and receive an explainable risk score with percentage-based contributing factors.</p><div className="hero-tags"><span>Image + video analysis</span><span>Explainable scoring</span></div></div><div className="hero-stat"><small>Latest risk</small><strong>{analyses[0]?.risk_score ?? 0}%</strong><span>{analyses[0]?.risk_level ?? "No analysis yet"}</span><em>{analyses.length ? "Updated from saved inspections" : "Run an inspection to begin"}</em></div></section>
        <section className="dashboard-section"><div className="section-heading"><div><span className="eyebrow">Overview</span><h2>Inspection health</h2></div><span className="section-caption">Live database summary</span></div><div className="overview-grid dashboard-overview"><div className="metric-card accent"><div className="metric-heading"><span>Saved analyses</span><i>01</i></div><strong>{analyses.length}</strong><small>Stored in database</small></div><div className="metric-card"><div className="metric-heading"><span>Average risk</span><i>02</i></div><strong>{averageRisk}%</strong><small>Across all inspections</small></div><div className="metric-card alert-metric"><div className="metric-heading"><span>High risk events</span><i>03</i></div><strong>{highRisk}</strong><small>Require attention</small></div></div></section>
        <section className="dashboard-section workflow-section"><div className="section-heading"><div><span className="eyebrow">Workflows</span><h2>Start a new inspection</h2></div><span className="section-caption">Choose your source</span></div><div className="workflow-grid"><Link className="workflow-card" to="/analysis"><span className="workflow-icon">◉</span><div><span className="card-label">Still image</span><h3>Image analysis</h3><p>Inspect PPE, proximity, and unsafe conditions from one site photo.</p><span className="workflow-link">Open image analysis <b>→</b></span></div></Link><Link className="workflow-card featured" to="/video"><span className="workflow-icon">▶</span><div><span className="card-label">Frame sampling</span><h3>Video detection</h3><p>Scan a video and surface the highest observed safety risk.</p><span className="workflow-link">Open video detection <b>→</b></span></div></Link></div></section>
        <section className="dashboard-note panel"><span className="live-dot" /><div><strong>Continuous monitoring ready</strong><p>Your next inspection will appear in Analysis and History after processing.</p></div></section>
      </main>
    </div>
  );
}
