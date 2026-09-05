from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_html_shell_blocks_automatic_translation() -> None:
    html = (PROJECT_ROOT / "frontend" / "index.html").read_text()

    assert '<html lang="es" translate="no" class="notranslate">' in html
    assert '<meta name="google" content="notranslate" />' in html
    assert '<div id="root" translate="no" class="notranslate"></div>' in html


def test_react_root_has_fatal_error_recovery() -> None:
    main = (PROJECT_ROOT / "frontend" / "src" / "main.tsx").read_text()

    assert "<FatalErrorBoundary>" in main
    assert "onUncaughtError: showFatalFallback" in main
    assert 'document.getElementById("fatal-root")' in main
