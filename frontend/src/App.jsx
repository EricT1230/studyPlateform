import { BrowserRouter, Routes, Route, Link, NavLink } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Practice from "./pages/Practice";
import Review from "./pages/Review";
import Tutorial from "./pages/Tutorial";
import Browse from "./pages/Browse";
import Learn from "./pages/Learn";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/" className="nav-brand">
          <span className="dot" aria-hidden="true" />
          學習平台
        </Link>
        <NavLink to="/" end className="nav-link">儀表板</NavLink>
        <NavLink to="/learn" className="nav-link">學習</NavLink>
        <NavLink to="/practice" className="nav-link">練習</NavLink>
        <NavLink to="/review" className="nav-link">複習</NavLink>
        <NavLink to="/browse" className="nav-link">瀏覽</NavLink>
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
