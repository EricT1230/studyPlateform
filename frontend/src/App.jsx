import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Practice from "./pages/Practice";
import Tutorial from "./pages/Tutorial";
import Browse from "./pages/Browse";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="nav">
        <Link to="/">儀表板</Link>
        <Link to="/practice">練習</Link>
        <Link to="/browse">瀏覽</Link>
      </nav>
      <main className="main">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/practice" element={<Practice />} />
          <Route path="/tutorial/:subject/:topic" element={<Tutorial />} />
          <Route path="/browse" element={<Browse />} />
        </Routes>
      </main>
    </BrowserRouter>
  );
}
