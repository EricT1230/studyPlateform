import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { marked } from "marked";
import { getTutorial } from "../api/client";
import NotesPanel from "../components/NotesPanel";
import useLanguage from "../components/useLanguage";

export default function Tutorial() {
  const { subject, topic } = useParams();
  const { language, t } = useLanguage();
  const [html, setHtml] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    getTutorial(subject, topic, language)
      .then((tutorial) => {
        if (!active) return;
        setHtml(marked.parse(tutorial.markdown));
        setError(false);
      })
      .catch(() => {
        if (active) setError(true);
      });
    return () => {
      active = false;
    };
  }, [subject, topic, language]);

  if (error)
    return (
      <div>
        <p className="empty">{t.tutorialMissing}</p>
        <NotesPanel subject={subject} topic={topic} />
      </div>
    );
  if (!html) return <p className="loading">{t.loading}</p>;
  return (
    <div>
      <article className="tutorial" dangerouslySetInnerHTML={{ __html: html }} />
      <div style={{ marginTop: 16 }}>
        <NotesPanel subject={subject} topic={topic} />
      </div>
    </div>
  );
}
