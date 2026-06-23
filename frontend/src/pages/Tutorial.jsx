import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { marked } from "marked";
import { getTutorial } from "../api/client";

export default function Tutorial() {
  const { subject, topic } = useParams();
  const [html, setHtml] = useState("");
  const [error, setError] = useState(false);

  useEffect(() => {
    setError(false);
    getTutorial(subject, topic)
      .then((t) => setHtml(marked.parse(t.markdown)))
      .catch(() => setError(true));
  }, [subject, topic]);

  if (error) return <p>這個主題還沒有教學文章。</p>;
  return <div dangerouslySetInnerHTML={{ __html: html }} />;
}
