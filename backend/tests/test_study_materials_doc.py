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
