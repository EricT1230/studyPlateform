const BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

async function get(path) {
  const res = await fetch(`${BASE}${path}`);
  if (!res.ok) throw new Error(`GET ${path} -> ${res.status}`);
  return res.json();
}

export function getSubjects() {
  return get("/subjects");
}

export function getQuestions({ subject, topic, difficulty, onlyWrong } = {}) {
  const p = new URLSearchParams();
  if (subject) p.set("subject", subject);
  if (topic) p.set("topic", topic);
  if (difficulty) p.set("difficulty", difficulty);
  if (onlyWrong) p.set("only_wrong", "true");
  const qs = p.toString();
  return get(`/questions${qs ? `?${qs}` : ""}`);
}

export async function postAttempt(questionId, chosen) {
  const res = await fetch(`${BASE}/attempts`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question_id: questionId, chosen }),
  });
  if (!res.ok) throw new Error(`POST /attempts -> ${res.status}`);
  return res.json();
}

export function getStats() {
  return get("/stats");
}

export function getTutorial(subject, topic) {
  return get(`/tutorials/${subject}/${topic}`);
}
