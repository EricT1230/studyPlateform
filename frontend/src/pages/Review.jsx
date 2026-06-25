import { useEffect, useState } from "react";
import { getReview } from "../api/client";
import QuestionCard from "../components/QuestionCard";
import NotesPanel from "../components/NotesPanel";

export default function Review() {
  const [queue, setQueue] = useState(null); // null = loading
  const [idx, setIdx] = useState(0);

  useEffect(() => {
    getReview().then(setQueue);
  }, []);

  if (queue === null) return <p className="loading">載入中…</p>;

  const current = queue[idx];

  return (
    <div>
      <h2>複習</h2>

      {queue.length === 0 && (
        <p className="empty">今天沒有要複習的，去「練習」刷新題吧。</p>
      )}

      {queue.length > 0 && !current && (
        <div className="banner"><p>今天複習完成 🎉 共 {queue.length} 題。</p></div>
      )}

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
