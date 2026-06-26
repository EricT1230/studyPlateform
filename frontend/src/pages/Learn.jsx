import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { getQuestions, getSubjects } from "../api/client";

export default function Learn() {
  const [subjects, setSubjects] = useState([]);
  const [questions, setQuestions] = useState([]);

  useEffect(() => {
    Promise.all([getSubjects(), getQuestions()]).then(([subjectList, questionList]) => {
      setSubjects(subjectList);
      setQuestions(questionList);
    });
  }, []);

  const counts = useMemo(() => {
    const byTopic = new Map();
    for (const q of questions) {
      const key = `${q.subject}/${q.topic}`;
      byTopic.set(key, (byTopic.get(key) || 0) + 1);
    }
    return byTopic;
  }, [questions]);

  if (subjects.length === 0) return <p className="loading">載入中…</p>;

  return (
    <div>
      <h2>學習</h2>
      <div className="learn-grid">
        {subjects.map((subject) => (
          <section className="learn-section" key={subject.subject}>
            <div className="learn-section-head">
              <h3>{subject.subject}</h3>
              <span className="tag">{subject.topics.length} topics</span>
            </div>
            <div className="learn-topic-list">
              {subject.topics.map((topic) => {
                const total = counts.get(`${subject.subject}/${topic}`) || 0;
                return (
                  <div className="learn-topic" key={topic}>
                    <div>
                      <Link className="learn-topic-title" to={`/tutorial/${subject.subject}/${topic}`}>
                        {topic}
                      </Link>
                      <div className="card-meta">
                        <span className="tag">{total} 題</span>
                      </div>
                    </div>
                    <div className="learn-actions">
                      <Link className="tag tag-link" to={`/tutorial/${subject.subject}/${topic}`}>
                        看教學
                      </Link>
                      <Link
                        className="tag tag-link"
                        to={`/practice?subject=${encodeURIComponent(subject.subject)}&topic=${encodeURIComponent(topic)}`}
                      >
                        練習
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </section>
        ))}
      </div>
    </div>
  );
}
