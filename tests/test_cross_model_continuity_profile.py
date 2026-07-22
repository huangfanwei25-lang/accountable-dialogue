from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "docs" / "contracts" / "cross-model-continuity-profile-v0.md"
ENTRYPOINTS = (
    ROOT / "CLAUDE.md",
    ROOT / "GEMINI.md",
    ROOT / ".github" / "copilot-instructions.md",
)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def test_profile_keeps_change_case_v0_as_its_only_cross_repository_payload_contract() -> None:
    profile = read(PROFILE)

    assert "accountable-dialogue/change-case-v0" in profile
    assert "schemas/change-case-v0.schema.json" in profile
    assert "唯一跨倉庫公共交換協議" in profile
    assert "直接 Python package dependency" in profile


def test_profile_separates_repository_ownership_and_private_import_boundary() -> None:
    profile = read(PROFILE)

    for owner in ("Accountable Dialogue", "Private Memory", "ToneSoul"):
        assert owner in profile
    assert "自動同步" in profile
    assert "私人資料匯入" in profile
    assert "chain-of-thought" in profile


def test_profile_bounds_deliberative_stance_and_resource_observation() -> None:
    profile = read(PROFILE)

    for public_item in (
        "承諾",
        "未解張力",
        "不確定性",
        "風險",
        "禁止推論",
        "改變條件",
    ):
        assert public_item in profile
    assert "`reported`" in profile
    assert "`not_reported`" in profile
    assert "token budget" in profile
    assert "identity" in profile


def test_cross_model_entrypoints_are_thin_public_only_adapters() -> None:
    agents = read(ROOT / "AGENTS.md")
    assert "PUBLIC_BOUNDARY.md" in agents
    assert "cross-model-continuity-profile-v0.md" in agents
    assert "不要求私人 Memory" in agents

    forbidden_private_routes = (
        "START_HERE.md",
        "owner_context",
        "historical_intake",
        "Memory.git",
        "C:\\Users\\",
    )
    for path in ENTRYPOINTS:
        adapter = read(path)
        assert "AGENTS.md" in adapter
        assert len(adapter.splitlines()) <= 12
        assert not any(route in adapter for route in forbidden_private_routes)

    assert read(ROOT / "CLAUDE.md").startswith("@AGENTS.md")
    assert read(ROOT / "GEMINI.md").startswith("@./AGENTS.md")


def test_readme_routes_readers_to_the_public_profile() -> None:
    readme = read(ROOT / "README.md")

    assert "docs/contracts/cross-model-continuity-profile-v0.md" in readme
