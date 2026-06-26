export const SUPPORTED_LANGUAGES = ["zh", "en"];

export const UI_TEXT = {
  zh: {
    appName: "刷題平台",
    dashboard: "首頁",
    learn: "學習",
    practice: "練習",
    review: "複習",
    browse: "題庫",
    loading: "載入中...",
    topics: "topics",
    questions: "題",
    tutorial: "教學",
    startPractice: "練習",
    tutorialMissing: "這個主題還沒有教學內容。",
    switchLanguage: "切換到英文",
    languageShort: "中",
    nextLanguageShort: "EN",
  },
  en: {
    appName: "Study Drill",
    dashboard: "Dashboard",
    learn: "Learn",
    practice: "Practice",
    review: "Review",
    browse: "Question Bank",
    loading: "Loading...",
    topics: "topics",
    questions: "questions",
    tutorial: "Tutorial",
    startPractice: "Practice",
    tutorialMissing: "Tutorial content is not available for this topic.",
    switchLanguage: "Switch to Chinese",
    languageShort: "EN",
    nextLanguageShort: "中",
  },
};

export function normalizeLanguage(value) {
  return SUPPORTED_LANGUAGES.includes(value) ? value : "zh";
}
