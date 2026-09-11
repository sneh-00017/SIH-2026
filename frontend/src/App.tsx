import { Navigate, Route, Routes } from "react-router-dom";
import HomePage from "./pages/HomePage";
import HistoryPage from "./pages/HistoryPage";
import DashboardPage from "./pages/DashboardPage";
import VideoPage from "./pages/VideoPage";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<DashboardPage />} />
      <Route path="/dashboard" element={<DashboardPage />} />
      <Route path="/analysis" element={<HomePage />} />
      <Route path="/video" element={<VideoPage />} />
      <Route path="/history" element={<HistoryPage />} />
      <Route path="/login" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
