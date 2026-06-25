import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
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
        className="search"
        placeholder="🔍 搜尋題目或 id…"
        value={q}
        onChange={(e) => setQ(e.target.value)}
      />
      {filtered.length === 0 && <p className="empty">找不到符合「{q}」的題目。</p>}
      {filtered.map((item) => (
        <div className="card" key={item.id}>
          <div className="card-meta">
            <span className="tag">{item.id}</span>
            <span className="tag">{item.subject}</span>
            <span className="tag">{item.difficulty}</span>
            <Link className="tag tag-link" to={`/tutorial/${item.subject}/${item.topic}`}>
              📖 看教學
            </Link>
          </div>
          <p className="browse-q">{item.question}</p>
          <ul className="browse-opts">
            {item.options.map((opt, idx) => (
              <li key={idx} className={idx === item.answer ? "is-answer" : ""}>
                {opt}{idx === item.answer ? "  ✅" : ""}
              </li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
