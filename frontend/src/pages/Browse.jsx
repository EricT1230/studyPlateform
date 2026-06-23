import { useEffect, useState } from "react";
import { getQuestions } from "../api/client";

export default function Browse() {
  const [questions, setQuestions] = useState([]);
  const [q, setQ] = useState("");

  useEffect(() => {
    getQuestions().then(setQuestions);
  }, []);

  const filtered = questions.filter((item) =>
    item.question.toLowerCase().includes(q.toLowerCase()) ||
    item.id.toLowerCase().includes(q.toLowerCase())
  );

  return (
    <div>
      <h2>瀏覽題庫 ({questions.length})</h2>
      <input
        placeholder="搜尋題目或 id…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        style={{ width: "100%", padding: 10, marginBottom: 16 }}
      />
      {filtered.map((item) => (
        <div className="card" key={item.id}>
          <div style={{ color: "#888", fontSize: 13 }}>
            {item.id} · {item.subject} · {item.difficulty}
          </div>
          <p style={{ whiteSpace: "pre-wrap" }}>{item.question}</p>
          <ul>
            {item.options.map((opt, idx) => (
              <li key={idx} style={{ fontWeight: idx === item.answer ? 700 : 400 }}>
                {opt}{idx === item.answer ? "  ✅" : ""}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
