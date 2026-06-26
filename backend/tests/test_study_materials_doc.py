from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CONTENT_DIR = REPO_ROOT / "content"
MATERIALS_DOC = REPO_ROOT / "docs" / "study-materials.md"


def test_study_materials_doc_covers_every_content_topic():
    assert MATERIALS_DOC.exists()

    markdown = MATERIALS_DOC.read_text(encoding="utf-8")
    missing = []

    for yaml_file in sorted(CONTENT_DIR.glob("*/*.yaml")):
        chapter_heading = f"### {yaml_file.parent.name}/{yaml_file.stem}"
        if chapter_heading not in markdown:
            missing.append(chapter_heading)

    assert missing == []


def test_study_materials_doc_has_actionable_learning_structure():
    assert MATERIALS_DOC.exists()

    markdown = MATERIALS_DOC.read_text(encoding="utf-8")
    required_sections = [
        "## 使用方式",
        "## 教材設計原則",
        "## 科目教材",
        "## 參考教材來源",
    ]
    missing = [section for section in required_sections if section not in markdown]

    assert missing == []
    assert "學習目標" in markdown
    assert "刷題策略" in markdown
    assert "常見誤區" in markdown


def test_study_materials_doc_has_completeness_table_and_visual_aids():
    assert MATERIALS_DOC.exists()

    markdown = MATERIALS_DOC.read_text(encoding="utf-8")
    required_fragments = [
        "## 完整性檢核",
        "## 圖表索引",
        "| 科目 | 目前章節 | 參考基準 | 完整性判斷 | 圖表輔助 |",
        "```mermaid",
        "讀書循環",
        "演算法選型",
        "系統堆疊",
        "資料庫查詢",
        "ML 評估",
    ]
    missing = [
        fragment for fragment in required_fragments if fragment not in markdown
    ]

    assert missing == []
    assert markdown.count("```mermaid") >= 6

    subjects = sorted(
        path.name
        for path in CONTENT_DIR.iterdir()
        if path.is_dir() and any(path.glob("*.yaml"))
    )
    missing_subject_rows = [
        subject for subject in subjects if f"| {subject} |" not in markdown
    ]

    assert missing_subject_rows == []
