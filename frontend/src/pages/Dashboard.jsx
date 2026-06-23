import { useEffect, useState } from "react";
import { getStats } from "../api/client";

export default function Dashboard() {
  const [stats, setStats] = useState(null);

  useEffect(() => {
    getStats().then(setStats);
  }, []);

  if (!stats) return <p>載入中…</p>;

  const attempted = stats.by_subject.reduce((n, r) => n + r.attempted, 0);

  return (
    <div>
      <h2>儀表板</h2>
      {attempted === 0 && <p style={{ color: "#888" }}>還沒有作答紀錄。去「練習」開始第一題吧！</p>}

      <div className="card">
        <h3>各科正確率</h3>
        {stats.by_subject.length === 0 && <p style={{ color: "#888" }}>—</p>}
        {stats.by_subject.map((r) => (
          <div className="stat-row" key={r.subject}>
            <span>{r.subject}</span>
            <span>{r.correct}/{r.attempted} ({Math.round(r.accuracy * 100)}%)</span>
          </div>
        ))}
      </div>

      <div className="card">
        <h3>最常錯的題目</h3>
        {stats.weakest_questions.length === 0 && <p style={{ color: "#888" }}>—</p>}
        {stats.weakest_questions.map((q) => (
          <div className="stat-row" key={q.question_id}>
            <span>{q.question_id}</span>
            <span>錯 {q.wrong} / 共 {q.total} 次</span>
          </div>
        ))}
      </div>
    </div>
  );
}
