import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { marked } from "marked";
import { getTutorial } from "../api/client";
import NotesPanel from "../components/NotesPanel";

export default function Tutorial() {
  const { subject, topic } = useParams();
  const [html, setHtml] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    getTutorial(subject, topic)
      .then((t) => {
        if (!active) return;
        setHtml(marked.parse(t.markdown));
        setError(false);
      })
      .catch(() => {
        if (active) setError(true);
      });
    return () => {
      active = false;
    };
  }, [subject, topic]);

  if (error)
    return (
      <div>
        <p className="empty">這個主題還沒有教學文章。</p>
        <NotesPanel subject={subject} topic={topic} />
      </div>
    );
  if (!html) return <p className="loading">載入中…</p>;
  return (
    <div>
      <article className="tutorial" dangerouslySetInnerHTML={{ __html: html }} />
      <div style={{ marginTop: 16 }}>
        <NotesPanel subject={subject} topic={topic} />
      </div>
    </div>
  );
}
