import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import Sidebar from "../components/Sidebar";
import { API_BASE_URL } from "../api/client";

type Analysis = { id: number; media_type: string; filename: string; risk_score: number; risk_level: string; created_at: string };

export default function HistoryPage() {
  const [history, setHistory] = useState<Analysis[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/api/analyses`)
      .then((response) => response.json())
      .then((data: { analyses?: Analysis[] }) => setHistory(data.analyses ?? []))
      .catch(() => setHistory([]))
      .finally(() => setLoading(false));
  }, []);

  const average = history.length ? Math.round(history.reduce((total, item) => total + item.risk_score, 0) / history.length) : 0;
  const highRisk = history.filter((item) => item.risk_level === "HIGH").length;
  const statusClass = (level: string) => level === "HIGH" ? "alert" : level === "MEDIUM" ? "warn" : "safe";
  const formatTime = (value: string) => new Date(value).toLocaleString([], { dateStyle: "medium", timeStyle: "short" });

  return <div className="app-shell"><Sidebar /><main className="dashboard-card history-page"><header className="page-heading"><div><span className="eyebrow">Audit trail</span><h1>Analysis history</h1><p>Stored image and video assessments from the SafeSight database.</p></div><Link className="outline-btn" to="/analysis">New analysis</Link></header><section className="history-summary"><div><span>Total analyses</span><strong>{history.length}</strong></div><div><span>Average risk</span><strong>{average}%</strong></div><div><span>High risk events</span><strong>{highRisk}</strong></div></section><section className="history-table panel"><div className="table-heading"><span>File</span><span>Stored at</span><span>Risk score</span><span>Status</span></div>{loading ? <p className="history-empty">Loading saved analyses...</p> : history.length === 0 ? <p className="history-empty">No analyses stored yet. Run an image or video analysis to create your first record.</p> : history.map((item) => <div className="history-row" key={item.id}><strong>{item.filename}<small>{item.media_type}</small></strong><span>{formatTime(item.created_at)}</span><div className="row-score"><i style={{ width: `${item.risk_score}%` }} /><b>{item.risk_score}%</b></div><span className={`history-pill ${statusClass(item.risk_level)}`}>{item.risk_level}</span></div>)}</section></main></div>;
}