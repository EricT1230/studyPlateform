const DIFFICULTIES = ["basic", "intermediate", "advanced", "master"];

export default function Filters({ subjects, value, onChange }) {
  const topics = subjects.find((s) => s.subject === value.subject)?.topics || [];
  return (
    <div className="filters">
      <select
        value={value.subject}
        onChange={(e) => onChange({ ...value, subject: e.target.value, topic: "" })}
      >
        <option value="">全部科目</option>
        {subjects.map((s) => (
          <option key={s.subject} value={s.subject}>{s.subject}</option>
        ))}
      </select>

      <select
        value={value.topic}
        onChange={(e) => onChange({ ...value, topic: e.target.value })}
        disabled={!value.subject}
      >
        <option value="">全部主題</option>
        {topics.map((t) => (
          <option key={t} value={t}>{t}</option>
        ))}
      </select>

      <select
        value={value.difficulty}
        onChange={(e) => onChange({ ...value, difficulty: e.target.value })}
      >
        <option value="">全部難度</option>
        {DIFFICULTIES.map((d) => (
          <option key={d} value={d}>{d}</option>
        ))}
      </select>

      <label>
        <input
          type="checkbox"
          checked={value.onlyWrong}
          onChange={(e) => onChange({ ...value, onlyWrong: e.target.checked })}
        />
        只練我錯過的
      </label>
    </div>
  );
}
