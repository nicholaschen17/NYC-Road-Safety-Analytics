import { NavLink, Route, Routes } from "react-router-dom";
import HotspotDashboard from "./pages/HotspotDashboard";
import IncidentExplorer from "./pages/IncidentExplorer";
import ZoneDrilldown from "./pages/ZoneDrilldown";
import ReportingCenter from "./pages/ReportingCenter";

const navLinkClass = ({ isActive }: { isActive: boolean }) =>
  isActive ? "active" : "";

export default function App() {
  return (
    <div className="app-shell">
      <nav className="app-nav" aria-label="Primary">
        <NavLink to="/" className={navLinkClass} end>
          Hotspot dashboard
        </NavLink>
        <NavLink to="/incidents" className={navLinkClass}>
          Incident explorer
        </NavLink>
        <NavLink to="/zones/row-93hm-56nh~k67y" className={navLinkClass}>
          Zone drill-down
        </NavLink>
        <NavLink to="/reporting" className={navLinkClass}>
          Reporting &amp; export
        </NavLink>
      </nav>
      <main className="app-main">
        <Routes>
          <Route path="/" element={<HotspotDashboard />} />
          <Route path="/incidents" element={<IncidentExplorer />} />
          <Route path="/zones/:gridId" element={<ZoneDrilldown />} />
          <Route path="/reporting" element={<ReportingCenter />} />
        </Routes>
      </main>
    </div>
  );
}
