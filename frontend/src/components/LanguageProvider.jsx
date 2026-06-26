import { useMemo, useState } from "react";
import { normalizeLanguage, UI_TEXT } from "../i18n";
import { LanguageContext } from "./languageContext";

const STORAGE_KEY = "study-platform-language";

function readStoredLanguage() {
  if (typeof window === "undefined") return "zh";
  return normalizeLanguage(window.localStorage.getItem(STORAGE_KEY));
}

export default function LanguageProvider({ children }) {
  const [language, setLanguageState] = useState(readStoredLanguage);

  function setLanguage(nextLanguage) {
    const normalized = normalizeLanguage(nextLanguage);
    setLanguageState(normalized);
    window.localStorage.setItem(STORAGE_KEY, normalized);
  }

  const value = useMemo(
    () => ({
      language,
      setLanguage,
      t: UI_TEXT[language],
    }),
    [language],
  );

  return (
    <LanguageContext.Provider value={value}>
      {children}
    </LanguageContext.Provider>
  );
}
