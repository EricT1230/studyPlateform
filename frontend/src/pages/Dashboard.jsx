import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { getStats } from "../api/client";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats().then(setStats);
  }, []);

  if (!stats) return <p className="loading">載入中…</p>;

  const attempted = stats.by_subject.reduce((n, r) => n + r.attempted, 0);

  return (
    <div>
      <h2>儀表板</h2>

      <div className="card">
        <h3>今天待複習</h3>
        <div className="stat-row">
          <span>到期題數</span>
          <span className="num">{stats.due_today} 題</span>
        </div>
        {stats.due_today > 0 && (
          <p style={{ marginTop: 16, marginBottom: 0 }}>
            <Link className="primary" to="/review">開始複習 →</Link>
          </p>
        )}
      </div>

      {attempted === 0 && (
        <div className="banner">
          <p>還沒有作答紀錄 — 去「練習」開始第一題，正確率與弱點分析會出現在這裡 ✨</p>
        </div>
      )}

      <div className="card">
        <h3>各科正確率</h3>
        {stats.by_subject.length === 0 && <p className="empty">—</p>}
        {stats.by_subject.map((r) => {
          const pct = Math.round(r.accuracy * 100);
          return (
            <div className="stat" key={r.subject}>
              <div className="stat-head">
                <span className="stat-name">{r.subject}</span>
                <span className="stat-val">{r.correct}/{r.attempted} · {pct}%</span>
              </div>
              <div className="bar"><i style={{ width: `${pct}%` }} /></div>
            </div>
          );
        })}
      </div>

      <div className="card">
        <h3>最常錯的題目</h3>
        {stats.weakest_questions.length === 0 && <p className="empty">—</p>}
        {stats.weakest_questions.map((q) => (
          <div className="stat-row" key={q.question_id}>
            <span className="tag">{q.question_id}</span>
            <span className="num">錯 {q.wrong} / 共 {q.total} 次</span>
          </div>
        ))}
      </div>
    </div>
  );
}
