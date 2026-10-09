"""Structural guarantees for the cuda11.8 PKGBUILD and its AUR metadata.

These encode two concrete defects found in the repository: .SRCINFO advertised a
completely different package (cuda11.4) than the PKGBUILD, and the packaged
toolchain must stay consistent with the CUDA 11.8 the package name promises.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from conftest import (
    REPO_ROOT,
    pkgbuild_array,
    pkgbuild_assignments,
    pkgbuild_scalar,
    read_pkgbuild,
)

PKGBUILD = read_pkgbuild()
SRCINFO = (REPO_ROOT / ".SRCINFO").read_text(encoding="utf-8")

EXPECTED_PKGVER = "11.8.0"
EXPECTED_DRIVER = "520.61.05"


def test_srcinfo_pkgbase_matches_pkgbase() -> None:
    """AUR clients read .SRCINFO, so it must not describe another package."""
    pkgbase = pkgbuild_scalar(PKGBUILD, "pkgbase")
    assert pkgbase == "cuda11.8"
    assert f"pkgbase = {pkgbase}" in SRCINFO


def test_srcinfo_pkgver_matches_pkgbuild() -> None:
    """A stale .SRCINFO would make AUR advertise the wrong version."""
    pkgver = pkgbuild_scalar(PKGBUILD, "pkgver")
    assert pkgver == EXPECTED_PKGVER
    assert f"pkgver = {pkgver}" in SRCINFO


def test_srcinfo_does_not_mention_the_old_package() -> None:
    """Regression guard for the cuda11.4 metadata that shipped here."""
    assert "cuda11.4" not in SRCINFO, (
        ".SRCINFO still advertises cuda11.4; regenerate with "
        "'makepkg --printsrcinfo'"
    )


def test_srcinfo_pkgname_entries_match_pkgname_array() -> None:
    """.SRCINFO must list exactly the packages the PKGBUILD splits into."""
    names = pkgbuild_array(PKGBUILD, "pkgname")
    assert names == ["cuda11.8", "cuda11.8-tools"]
    for name in names:
        assert f"pkgname = {name}" in SRCINFO, f"{name} missing from .SRCINFO"


def _expand(text: str, variables: dict[str, str]) -> str:
    """Resolve ``$var`` / ``${var}`` references the way makepkg would."""
    for name, value in variables.items():
        text = text.replace("${" + name + "}", value).replace("$" + name, value)
    return text


def test_source_url_uses_the_official_https_endpoint() -> None:
    """The installer must come from NVIDIA over HTTPS and match the version."""
    source = pkgbuild_array(PKGBUILD, "source")
    installer = next((s for s in source if s.endswith("_linux.run")), None)
    assert installer is not None, "no installer source entry found"
    assert installer.startswith("https://"), (
        f"installer is fetched over an insecure scheme: {installer}"
    )
    assert "developer.download.nvidia.com" in installer

    # The entry is written with ${pkgver}/${_driverver}; expand it before
    # asserting on the concrete filename so the test checks the real download.
    expanded = _expand(
        installer,
        {"pkgver": EXPECTED_PKGVER, "_driverver": EXPECTED_DRIVER},
    )
    assert expanded.endswith(f"cuda_{EXPECTED_PKGVER}_{EXPECTED_DRIVER}_linux.run"), (
        f"installer resolves to an unexpected filename: {expanded}"
    )
    assert "$" not in expanded, f"installer URL has an unresolved variable: {expanded}"


def test_every_source_has_a_checksum_or_is_skipped() -> None:
    """Each source needs a matching checksum entry, or makepkg cannot verify."""
    source = pkgbuild_array(PKGBUILD, "source")
    sums = pkgbuild_array(PKGBUILD, "sha512sums")
    assert len(sums) == len(source), (
        f"{len(source)} sources but {len(sums)} sha512sums; makepkg will refuse"
    )
    assert all(re.fullmatch(r"[0-9a-f]{128}", s) for s in sums), (
        "every sha512sum must be a full 128-char hex digest"
    )


def test_packaged_toolchain_targets_cuda_11_8() -> None:
    """The .pc files must describe the toolkit this package actually ships."""
    for pc in ("cuda.pc", "cudart.pc"):
        text = (REPO_ROOT / pc).read_text(encoding="utf-8")
        assert "/opt/cuda" in text, f"{pc} must reference the /opt/cuda prefix"
        assert "cudaroot=/opt/cuda\n" in text + "\n", (
            f"{pc} cudaroot should point at /opt/cuda"
        )


def test_cuda_pc_reports_major_version_11() -> None:
    """Nonsensical version metadata breaks pkg-config consumers."""
    text = (REPO_ROOT / "cuda.pc").read_text(encoding="utf-8")
    match = re.search(r"^Version:\s*(\S+)", text, re.MULTILINE)
    assert match is not None, "cuda.pc has no Version field"
    assert match.group(1).startswith("11"), (
        f"cuda.pc advertises CUDA {match.group(1)}, expected an 11.x version"
    )


def test_install_hook_refreshes_the_loader_cache() -> None:
    """A toolkit that links into /opt/cuda needs ldconfig after install."""
    text = (REPO_ROOT / "cuda.install").read_text(encoding="utf-8")
    assert "post_install" in text
    assert "ldconfig" in text, (
        "cuda.install must run ldconfig so the new libs are findable"
    )


def test_profile_script_exports_cuda_path() -> None:
    """Without CUDA_PATH/PATH the toolkit is not discoverable after install."""
    text = (REPO_ROOT / "cuda.sh").read_text(encoding="utf-8")
    assert "CUDA_PATH=/opt/cuda" in text
    assert "/opt/cuda/bin" in text


@pytest.mark.parametrize("field", ["depends", "options", "license", "arch"])
def test_required_metadata_fields_are_present(field: str) -> None:
    """makepkg rejects a PKGBUILD missing these fields."""
    assignments = pkgbuild_assignments()
    assert field in assignments, f"PKGBUILD is missing {field}"
