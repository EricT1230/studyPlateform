import { useEffect, useState } from "react";
import { getNotes, saveNotes } from "../api/client";

export default function NotesPanel({ subject, topic }) {
  const [open, setOpen] = useState(false);
  const [text, setText] = useState("");
  const [status, setStatus] = useState("");

  useEffect(() => {
    if (!subject || !topic) return;
    getNotes(subject, topic).then((n) => setText(n.markdown));
  }, [subject, topic]);

  async function save() {
    setStatus("儲存中…");
    await saveNotes(subject, topic, text);
    setStatus("已儲存 ✓");
    setTimeout(() => setStatus(""), 1500);
  }

  if (!subject || !topic) return null;

  return (
    <div className={`card notes-panel ${open ? "is-open" : ""}`}>
      <button className="notes-toggle" onClick={() => setOpen((o) => !o)}>
        <span>✍️ 筆記（{subject} · {topic}）</span>
        <span aria-hidden="true">{open ? "▲" : "▼"}</span>
      </button>
      {open && (
        <div className="notes-body">
          <textarea
            className="notes-area"
            value={text}
            onChange={(e) => setText(e.target.value)}
            placeholder="寫下這個主題的筆記（Markdown）…"
          />
          <div className="notes-actions">
            <button className="primary" onClick={save}>儲存筆記</button>
            <span className="notes-status">{status}</span>
          </div>
        </div>
      )}
    </div>
  );
}
