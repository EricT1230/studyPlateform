import { useEffect, useState } from "react";
import { getSubjects, getQuestions } from "../api/client";
import Filters from "../components/Filters";
import QuestionCard from "../components/QuestionCard";

const EMPTY = { subject: "", topic: "", difficulty: "", onlyWrong: false };

export default function Practice() {
  const [subjects, setSubjects] = useState([]);
  const [filters, setFilters] = useState(EMPTY);
  const [queue, setQueue] = useState([]);
  const [idx, setIdx] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSubjects().then(setSubjects);
  }, []);

  async function start() {
    setLoading(true);
    const qs = await getQuestions({
      subject: filters.subject,
      topic: filters.topic,
      difficulty: filters.difficulty,
      onlyWrong: filters.onlyWrong,
    });
    // shuffle for variety
    setQueue([...qs].sort(() => Math.random() - 0.5));
    setIdx(0);
    setLoading(false);
  }

  const current = queue[idx];

  return (
    <div>
      <h2>練習</h2>
      <Filters subjects={subjects} value={filters} onChange={setFilters} />
      <button className="primary" onClick={start}>開始練習</button>

      {loading && <p>載入中…</p>}
      {!loading && queue.length > 0 && !current && <p>本輪結束 🎉 共 {queue.length} 題。</p>}
      {!loading && queue.length === 0 && <p style={{ color: "#888" }}>選好條件後按「開始練習」。</p>}

      {current && (
        <>
          <p style={{ color: "#888" }}>第 {idx + 1} / {queue.length} 題</p>
          <QuestionCard
            key={current.id}
            question={current}
            onAnswered={() => setIdx((i) => i + 1)}
          />
        </>
      )}
    </div>
  );
}
