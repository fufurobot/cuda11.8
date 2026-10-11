"""Secret-hygiene guarantees for the packaging repos.

The .env spec is strict: real credentials must never reach the public remote,
and any file a tool reads for credentials must be ignored *before* it exists in
the working tree. These tests encode that contract so a future edit cannot
quietly reintroduce a leak.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

from conftest import REPO_ROOT, git_tracked_files

SECRET_FILES = (".env",)


def _git_check_ignore(repo: Path, path: str) -> bool:
    """True when git would ignore ``path`` inside ``repo``.

    ``--no-index`` is required: without it git only reports a path as ignored
    when it actually exists in the working tree, so the check would pass
    locally and fail in a fresh CI clone.
    """
    result = subprocess.run(
        ["git", "-C", str(repo), "check-ignore", "--no-index", "--quiet", path],
        capture_output=True,
    )
    # 0 == ignored, 1 == not ignored, other == error.
    return result.returncode == 0


@pytest.mark.parametrize("secret", SECRET_FILES)
def test_env_file_is_ignored(secret: str) -> None:
    """.env must be ignored, or the token gets committed on the next `git add -A`."""
    assert _git_check_ignore(REPO_ROOT, secret), (
        f"{secret} is not ignored; a future 'git add -A' would publish the token"
    )


@pytest.mark.parametrize("secret", SECRET_FILES)
def test_env_file_is_never_tracked(secret: str) -> None:
    """The secret file must not be tracked, even if it was ignored later."""
    assert secret not in git_tracked_files(REPO_ROOT), (
        f"{secret} is tracked by git; the credential is already exposed"
    )


def test_env_example_exists_and_is_tracked() -> None:
    """A redacted template must exist and be committed for contributors."""
    example = REPO_ROOT / ".env.example"
    assert example.is_file(), ".env.example is missing"
    assert ".env.example" in git_tracked_files(REPO_ROOT), (
        ".env.example exists but is not tracked; it will not reach the remote"
    )


def test_env_example_contains_no_secret_values() -> None:
    """The template must not leak any real credential value."""
    text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    # A GitHub token of any shape must never appear in the template.
    for marker in ("github_pat_", "ghp_", "gho_", "ghs_", "ghu_"):
        assert marker not in text, f".env.example leaks a token ({marker})"


def test_env_example_documents_required_keys() -> None:
    """The keys the tooling reads must be documented, with empty values."""
    text = (REPO_ROOT / ".env.example").read_text(encoding="utf-8")
    assert "GITHUB_TOKEN=" in text, "GITHUB_TOKEN is not documented"
    for line in text.splitlines():
        if line.startswith("GITHUB_TOKEN="):
            assert line.strip() == "GITHUB_TOKEN=", (
                "GITHUB_TOKEN must be present but empty in the template"
            )


def test_gitattributes_export_ignores_secrets() -> None:
    """Defense in depth: secrets must be excluded from archives."""
    path = REPO_ROOT / ".gitattributes"
    assert path.is_file(), ".gitattributes is missing"
    text = path.read_text(encoding="utf-8")
    assert ".env export-ignore" in text, (
        ".env must be export-ignored so `git archive` cannot leak it"
    )


# Anything this large is certainly a build artifact and must never be
# committed: GitHub rejects a push whose pack exceeds 2 GiB, so a single stray
# file makes the repository unpushable.
MAX_TRACKED_FILE_BYTES = 64 * 1024 * 1024


def test_no_oversized_files_are_tracked() -> None:
    """Guard against committing build artifacts.

    A stray 3.7 GB split part was previously committed here by 'git add -A',
    which made every push fail with 'pack exceeds maximum allowed size'.
    """
    oversized = []
    for rel in git_tracked_files(REPO_ROOT):
        path = REPO_ROOT / rel
        if path.is_file() and path.stat().st_size > MAX_TRACKED_FILE_BYTES:
            oversized.append((rel, path.stat().st_size))
    assert not oversized, (
        f"tracked files exceed {MAX_TRACKED_FILE_BYTES} bytes: {oversized}"
    )


def test_pkgbuild_sources_are_ignored() -> None:
    """makepkg stages the multi-GB installer in-tree; it must never be added."""
    for name in (
        "cuda_11.8.0_520.61.05_linux.run",
        "cuda_11.8.0_520.61.05_linux.run.part-00",
        "cuda11.8-11.8.0-1-x86_64.pkg.tar.zst.part-00",
    ):
        assert _git_check_ignore(REPO_ROOT, name), (
            f"{name} is not ignored; 'git add -A' would commit a multi-GB file"
        )
