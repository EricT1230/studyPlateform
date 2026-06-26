import { useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { getSubjects, getQuestions } from "../api/client";
import Filters from "../components/Filters";
import QuestionCard from "../components/QuestionCard";
import NotesPanel from "../components/NotesPanel";

const EMPTY = { subject: "", topic: "", difficulty: "", onlyWrong: false };

export default function Practice() {
  const [searchParams] = useSearchParams();
  const [subjects, setSubjects] = useState([]);
  const [filters, setFilters] = useState(EMPTY);
  const [queue, setQueue] = useState([]);
  const [idx, setIdx] = useState(0);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getSubjects().then(setSubjects);
  }, []);

  useEffect(() => {
    const subject = searchParams.get("subject") || "";
    const topic = searchParams.get("topic") || "";
    if (subject || topic) {
      setFilters((current) => ({ ...current, subject, topic }));
    }
  }, [searchParams]);

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

      {loading && <p className="loading">載入中…</p>}
      {!loading && queue.length > 0 && !current && (
        <div className="banner"><p>本輪結束 🎉 共完成 {queue.length} 題，按上方「開始練習」再來一輪。</p></div>
      )}
      {!loading && queue.length === 0 && <p className="empty">選好條件後按「開始練習」。</p>}

      {current && (
        <>
          <div className="progress-meta">
            <span>第 {idx + 1} / {queue.length} 題</span>
            <div className="bar"><i style={{ width: `${(idx / queue.length) * 100}%` }} /></div>
          </div>
          <QuestionCard
            key={current.id}
            question={current}
            onAnswered={() => setIdx((i) => i + 1)}
          />
          <NotesPanel subject={current.subject} topic={current.topic} />
        </>
      )}
    </div>
  );
}
