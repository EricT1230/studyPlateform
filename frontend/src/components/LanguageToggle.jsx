import useLanguage from "./useLanguage";

export default function LanguageToggle() {
  const { language, setLanguage, t } = useLanguage();
  const nextLanguage = language === "zh" ? "en" : "zh";

  return (
    <button
      className="language-toggle"
      type="button"
      aria-label={t.switchLanguage}
      title={t.switchLanguage}
      onClick={() => setLanguage(nextLanguage)}
    >
      <span>{t.languageShort}</span>
      <strong>{t.nextLanguageShort}</strong>
    </button>
  );
}
