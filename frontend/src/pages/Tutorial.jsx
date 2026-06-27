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
  const [toc, setToc] = useState([]);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;
    getTutorial(subject, topic, language)
      .then((tutorial) => {
        if (!active) return;
        const doc = new DOMParser().parseFromString(
          marked.parse(tutorial.markdown),
          "text/html"
        );
        const items = [...doc.querySelectorAll("h2, h3")].map((h, i) => {
          h.id = `sec-${i}`;
          return { id: `sec-${i}`, text: h.textContent, sub: h.tagName === "H3" };
        });
        setToc(items);
        setHtml(doc.body.innerHTML);
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
    <div className="reading">
      <article className="tutorial" dangerouslySetInnerHTML={{ __html: html }} />
      <aside className="reading-side">
        {toc.length > 0 && (
          <nav className="toc card">
            <div className="toc-title">本章目錄</div>
            <ul>
              {toc.map((s) => (
                <li key={s.id} className={s.sub ? "toc-sub" : ""}>
                  <a href={`#${s.id}`}>{s.text}</a>
                </li>
              ))}
            </ul>
          </nav>
        )}
        <NotesPanel subject={subject} topic={topic} />
      </aside>
    </div>
  );
}
