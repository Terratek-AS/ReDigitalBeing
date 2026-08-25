from html.parser import HTMLParser
from pathlib import Path


STATIC_DIR = Path(__file__).parents[1] / "app" / "static"
OUT_DIR = Path(__file__).parents[2] / "out"


class _IdCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        del tag
        self.ids.extend(value for name, value in attrs if name == "id" and value is not None)


def test_admin_console_contains_governed_research_workflow() -> None:
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    required_ids = {
        "dashboard-admin",
        "admin-actor-id",
        "btn-admin-refresh",
        "btn-admin-export",
        "admin-kpi-users",
        "admin-kpi-review",
        "btn-admin-create-invite",
        "admin-invitations-list",
        "admin-users-list",
        "admin-questions-list",
        "admin-review-notes",
        "btn-admin-convert-scenario",
        "admin-scenarios-list",
        "admin-runs-list",
        "admin-run-observations",
        "admin-audit-list",
    }
    for element_id in required_ids:
        assert f'id="{element_id}"' in html

    assert 'data-open-role="admin"' in html
    assert "It is not production authentication" in html


def test_admin_console_javascript_wires_platform_endpoints_and_safe_rendering() -> None:
    javascript = (STATIC_DIR / "app.js").read_text(encoding="utf-8")
    required_contracts = {
        "/platform/users?actor_id=",
        "/platform/invitations?actor_id=",
        "/platform/research/questions?actor_id=",
        "/platform/scenarios?actor_id=",
        "/platform/runs?actor_id=",
        'api("/platform/audit"',
        "/convert-scenario",
        "/observations?actor_id=",
    }
    for contract in required_contracts:
        assert contract in javascript

    assert "escapeHtml(item.title)" in javascript
    assert "escapeHtml(item.description)" in javascript
    assert 'localStorage.setItem("roomzero_admin_actor_id"' in javascript
    assert "roomzero.research-export.v1" in javascript


def test_admin_console_has_responsive_workspace_styles() -> None:
    css = (STATIC_DIR / "styles.css").read_text(encoding="utf-8")
    for selector in (
        ".admin-console",
        ".admin-kpi-grid",
        ".admin-workspace-grid",
        ".admin-module",
        ".admin-split",
        ".audit-timeline",
        ".prototype-warning",
    ):
        assert selector in css


def test_pwa_icons_exist_and_match_declared_assets() -> None:
    html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    manifest = (STATIC_DIR / "manifest.json").read_text(encoding="utf-8")
    service_worker = (STATIC_DIR / "service-worker.js").read_text(encoding="utf-8")

    assert 'href="./icon-192.svg"' in html
    for filename in ("icon-192.svg", "icon-512.svg"):
        icon = STATIC_DIR / filename
        assert icon.stat().st_size > 500
        assert filename in manifest
        assert f"/static/{filename}" in service_worker


def test_admin_console_html_has_no_duplicate_ids() -> None:
    parser = _IdCollector()
    parser.feed((STATIC_DIR / "index.html").read_text(encoding="utf-8"))
    assert len(parser.ids) >= 100
    assert len(parser.ids) == len(set(parser.ids))


def test_static_release_artifact_matches_application_assets() -> None:
    for source in STATIC_DIR.iterdir():
        if source.is_file():
            release_asset = OUT_DIR / source.name
            assert release_asset.exists(), f"Missing release asset: {source.name}"
            assert release_asset.read_bytes() == source.read_bytes(), (
                f"Stale release asset: {source.name}"
            )
