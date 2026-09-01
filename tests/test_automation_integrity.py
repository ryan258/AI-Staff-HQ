"""Contract tests for the executable automation examples."""

import importlib.util
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
AUTOMATION_ROOT = PROJECT_ROOT / "workflows" / "automations"


@pytest.mark.parametrize(
    "relative_path",
    [
        Path("daily_news_summarizer.py"),
        Path("social_media_trend_tracker.py"),
        Path("concepts/summarize_new_articles_concept.py"),
    ],
)
def test_automation_sources_compile(relative_path):
    """Every checked-in automation source should at least be valid Python."""
    source_path = AUTOMATION_ROOT / relative_path
    compile(source_path.read_text(encoding="utf-8"), str(source_path), "exec")


@pytest.mark.parametrize(
    "relative_path",
    [Path("daily_news_summarizer.py"), Path("social_media_trend_tracker.py")],
)
def test_executable_automations_import(relative_path):
    """Executable automation modules must import in the project environment."""
    source_path = AUTOMATION_ROOT / relative_path
    module_name = f"automation_integrity_{source_path.stem}"
    spec = importlib.util.spec_from_file_location(module_name, source_path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)


def test_automation_dependencies_are_declared_in_project_metadata():
    """Runtime imports must be direct project dependencies, not transitive luck."""
    pyproject = (PROJECT_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"feedparser' in pyproject
    assert '"requests' in pyproject


def test_concept_automation_avoids_backslashes_inside_f_string_expressions():
    """Keep the illustrative script parseable on the supported Python range."""
    source = (AUTOMATION_ROOT / "concepts" / "summarize_new_articles_concept.py").read_text(
        encoding="utf-8"
    )
    assert "text[:30].replace('\\n', ' ')" not in source
