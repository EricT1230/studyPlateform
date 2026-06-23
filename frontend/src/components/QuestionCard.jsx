import { useState } from "react";
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
      <div style={{ color: "#888", fontSize: 13 }}>
        {question.subject} · {question.topic} · {question.difficulty}
      </div>
      <p style={{ whiteSpace: "pre-wrap", fontWeight: 600 }}>{question.question}</p>
      {question.options.map((opt, idx) => (
        <button key={idx} className={optionClass(idx)} onClick={() => choose(idx)}>
          {opt}
        </button>
      ))}
      {result && (
        <div className="explanation">
          <strong>{result.is_correct ? "✅ 答對了" : "❌ 答錯了"}</strong>
          <p style={{ whiteSpace: "pre-wrap" }}>{result.explanation}</p>
          <button className="primary" onClick={onAnswered}>下一題</button>
        </div>
      )}
    </div>
  );
}
