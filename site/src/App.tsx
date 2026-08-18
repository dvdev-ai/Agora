import { useEffect } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { Atmosphere } from "@/components/Atmosphere";
import { Footer, Header } from "@/components/Header";
import { HomePage } from "@/pages/HomePage";
import { ToolsPage } from "@/pages/ToolsPage";
import { DialoguePage } from "@/pages/DialoguePage";
import { PrivacyPage } from "@/pages/PrivacyPage";
import { StartPage } from "@/pages/StartPage";

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, left: 0, behavior: "instant" as ScrollBehavior });
  }, [pathname]);
  return null;
}

export default function App() {
  return (
    <div className="page-shell">
      <Atmosphere />
      <Header />
      <ScrollToTop />
      <main>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/tools" element={<ToolsPage />} />
          <Route path="/dialogue" element={<DialoguePage />} />
          <Route path="/privacy" element={<PrivacyPage />} />
          <Route path="/start" element={<StartPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
}
