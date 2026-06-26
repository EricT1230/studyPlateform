import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Practice from "./pages/Practice";
import Review from "./pages/Review";
import Tutorial from "./pages/Tutorial";
import Browse from "./pages/Browse";
import Learn from "./pages/Learn";
import LanguageToggle from "./components/LanguageToggle";
import LanguageProvider from "./components/LanguageProvider";
import useLanguage from "./components/useLanguage";

function AppShell() {
  const { t } = useLanguage();

  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/" className="nav-brand">
          <span className="dot" aria-hidden="true" />
          {t.appName}
        </Link>
        <NavLink to="/" end className="nav-link">{t.dashboard}</NavLink>
        <NavLink to="/learn" className="nav-link">{t.learn}</NavLink>
        <NavLink to="/practice" className="nav-link">{t.practice}</NavLink>
        <NavLink to="/review" className="nav-link">{t.review}</NavLink>
        <NavLink to="/browse" className="nav-link">{t.browse}</NavLink>
        <LanguageToggle />
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/learn" element={<Learn />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/review" element={<Review />} />
          <Route path="/tutorial/:subject/:topic" element={<Tutorial />} />
          <Route path="/browse" element={<Browse />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}

export default function App() {
  return (
    <LanguageProvider>
      <AppShell />
    </LanguageProvider>
  );
}
