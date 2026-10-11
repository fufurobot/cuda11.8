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


def test_packaged_toolchain_targets_a_versioned_prefix() -> None:
    """The toolkit installs side by side under /opt/cuda-11.8.

    Installing to /opt/cuda would collide with the distro cuda package, which
    owns that path. The cuda-11.1 reference package uses the same versioned
    convention.
    """
    for pc in ("cuda.pc", "cudart.pc"):
        text = (REPO_ROOT / pc).read_text(encoding="utf-8")
        assert "cudaroot=/opt/cuda-11.8\n" in text + "\n", (
            f"{pc} cudaroot should point at /opt/cuda-11.8"
        )
        # Guard against a regression to the unversioned, colliding path.
        assert "cudaroot=/opt/cuda\n" not in text + "\n", (
            f"{pc} must not use the shared /opt/cuda prefix"
        )


def test_pkgbuild_declares_a_single_cudaroot() -> None:
    """The install prefix must be defined once, not repeated inline."""
    assert "_cudaroot=/opt/cuda-11.8" in PKGBUILD, (
        "the PKGBUILD must declare _cudaroot, so the prefix cannot drift"
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
    assert "CUDA_PATH=/opt/cuda-11.8" in text
    assert "/opt/cuda-11.8/bin" in text


def test_ld_conf_points_at_the_correct_prefix() -> None:
    """A stale ld.so.conf path means the libraries are never found."""
    text = (REPO_ROOT / "cuda.conf").read_text(encoding="utf-8")
    assert text.startswith("/opt/cuda-11.8/lib64\n"), (
        "cuda.conf must list the versioned prefix first"
    )
    assert "\n/opt/cuda/lib64" not in "\n" + text, (
        "cuda.conf must not reference the shared /opt/cuda prefix"
    )


def test_install_hook_messages_match_the_prefix() -> None:
    """Misleading post_install output sends users to the wrong directory."""
    text = (REPO_ROOT / "cuda.install").read_text(encoding="utf-8")
    assert "/opt/cuda-11.8/bin" in text
    assert "/opt/cuda/bin" not in text


@pytest.mark.parametrize("field", ["depends", "options", "license", "arch"])
def test_required_metadata_fields_are_present(field: str) -> None:
    """makepkg rejects a PKGBUILD missing these fields."""
    assignments = pkgbuild_assignments()
    assert field in assignments, f"PKGBUILD is missing {field}"


def test_prepare_guards_the_samples_glob() -> None:
    """Regression: the findgllib glob must not run unguarded.

    CUDA 11.8 no longer bundles the samples, so
    ``builds/cuda_samples/*/*/findgllib.mk`` matches nothing. Without
    nullglob the literal pattern reaches `patch`, which then tries to create a
    file called "*" and fails prepare() outright.
    """
    text = PKGBUILD
    start = text.find("prepare() {")
    assert start != -1
    # Isolate prepare() only; build() legitimately does not need nullglob.
    end = text.find("\nbuild()", start)
    prepare_body = text[start:end]

    assert "nullglob" in prepare_body, (
        "prepare() must enable nullglob before globbing for findgllib.mk"
    )
    assert "_findgllib" in prepare_body, (
        "the glob result must be captured, not expanded inline in the for loop"
    )
    # The original bug: an inline unguarded glob in the for statement.
    assert "for f in builds/cuda_samples/*/*/findgllib.mk" not in prepare_body


def test_build_tolerates_a_missing_samples_tree() -> None:
    """build() must not assume cuda_samples exists (absent in CUDA 11.8)."""
    text = PKGBUILD
    start = text.find("build() {")
    end = text.find("\npackage_cuda11.8()", start)
    build_body = text[start:end]

    assert '[[ -d cuda_samples ]]' in build_body, (
        "build() must guard the cuda_samples move; CUDA 11.8 omits it"
    )
    # Hard-coded removal of a possibly-missing path aborts the build.
    assert "samples/bin/cuda-uninstaller" not in build_body or "rm -rf" in build_body


def test_tools_package_guards_optional_sample_paths() -> None:
    """cuda11.8-tools must not fail when the samples are absent."""
    text = PKGBUILD
    start = text.find("package_cuda11.8-tools()")
    assert start != -1
    body = text[start:]

    assert '[[ -d "${_prepdir}${_cudaroot}/samples" ]]' in body, (
        "the tools package must guard the samples move"
    )
    # A brace-expansion mv that includes a missing path fails outright.
    assert 'mv "${_prepdir}"/opt/cuda/{libnvvp,samples}' not in body


def test_pkgbuild_declares_side_by_side_provides() -> None:
    """provides/conflicts must not claim to replace the distro cuda package.

    The toolkit installs to a versioned prefix precisely so it can coexist with
    the distro `cuda` package. Claiming `provides=('cuda')` while also
    conflicting with it would make pacman refuse to install a package that is
    explicitly designed to sit alongside.
    """
    # Strip comments first: the PKGBUILD explains this decision in a comment
    # that itself mentions provides=('cuda').
    code = "\n".join(
        line for line in PKGBUILD.splitlines() if not line.lstrip().startswith("#")
    )
    assert "provides=('cuda'" not in code, (
        "cuda11.8 installs to a versioned prefix and must not claim provides=('cuda')"
    )
    assert "conflicts=('cuda'" not in code, (
        "cuda11.8 must not conflict with the distro cuda package"
    )
    # The versioned provides are the correct declaration.
    assert "provides=('cuda11.8-toolkit')" in code


def test_gitlab_ci_builds_the_package_with_makepkg(ci: dict | None = None) -> None:
    """The pipeline must actually run makepkg, not just lint the PKGBUILD."""
    import yaml

    class _L(yaml.SafeLoader):
        pass

    _L.add_constructor("!reference", lambda l, n: l.construct_sequence(n))
    data = yaml.load(
        (REPO_ROOT / ".gitlab-ci.yml").read_text(encoding="utf-8"), Loader=_L
    )
    text = "\n".join(
        str(step)
        for job, cfg in data.items()
        if isinstance(cfg, dict)
        for key in ("before_script", "script")
        for step in (cfg.get(key) or [])
    )
    assert "makepkg" in text, "the pipeline never invokes makepkg"
    assert "--noconfirm" in text, "makepkg would block on a prompt in CI"
