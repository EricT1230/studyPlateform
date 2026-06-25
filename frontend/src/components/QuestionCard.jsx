import { useState } from "react";
import { Link } from "react-router-dom";
import { postAttempt } from "../api/client";

export default function QuestionCard({ question, onAnswered }) {
  const [result, setResult] = useState(null); // { is_correct, answer, explanation }
  const [chosen, setChosen] = useState(null);

  async function choose(idx) {
    if (result) return; // already answered
    setChosen(idx);
    const r = await postAttempt(question.id, idx);
    setResult(r);
  }

  function optionClass(idx) {
    if (!result) return "option";
    if (idx === result.answer) return "option correct";
    if (idx === chosen) return "option wrong";
    return "option";
  }

  return (
    <div className="card">
      <div className="card-meta">
        <span className="tag">{question.subject}</span>
        <span className="tag">{question.topic}</span>
        <span className="tag">{question.difficulty}</span>
        <Link className="tag tag-link" to={`/tutorial/${question.subject}/${question.topic}`}>
          📖 看教學
        </Link>
      </div>
      <p className="question">{question.question}</p>
      {question.options.map((opt, idx) => (
        <button key={idx} className={optionClass(idx)} disabled={!!result} onClick={() => choose(idx)}>
          {opt}
        </button>
      ))}
      {result && (
        <div className="explanation">
          <strong className={`verdict ${result.is_correct ? "ok" : "bad"}`}>
            {result.is_correct ? "✅ 答對了" : "❌ 答錯了"}
          </strong>
          <p>{result.explanation}</p>
          <button className="primary" onClick={onAnswered}>下一題 →</button>
        </div>
      )}
    </div>
  );
}
