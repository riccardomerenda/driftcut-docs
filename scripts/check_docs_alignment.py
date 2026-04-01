"""Consistency checks for Driftcut docs release surfaces."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DOCS_ROOT = Path(__file__).resolve().parents[1]
VERSION_TAG_RE = re.compile(r"\bv(?P<version>\d+\.\d+\.\d+)\b")

VERSIONED_FILES = (
    Path("mkdocs.yml"),
    Path("docs/index.md"),
    Path("docs/configuration.md"),
    Path("docs/concept.md"),
)
TIERED_STALE_PHRASES = {
    Path("docs/index.md"): [
        "Real light-to-heavy escalation for judge calls",
    ],
    Path("docs/getting-started.md"): [
        "`judge_strategy: tiered` is currently a compatibility alias for `light` until real escalation lands.",
    ],
    Path("docs/configuration.md"): [
        "Currently behaves like `light` for compatibility. Real light-to-heavy escalation is still planned.",
    ],
    Path("docs/concept.md"): [
        "The next quality milestone is real light-to-heavy escalation",
        "Real automatic escalation from light to heavy is still the next milestone.",
    ],
    Path("docs/roadmap.md"): [
        "The next milestone is real light-to-heavy escalation.",
        "Real tiered light-to-heavy escalation",
    ],
}


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _find_versions(text: str) -> set[str]:
    return {f"v{match.group('version')}" for match in VERSION_TAG_RE.finditer(text)}


def _parse_version(tag: str) -> tuple[int, int, int]:
    major, minor, patch = tag.removeprefix("v").split(".")
    return int(major), int(minor), int(patch)


def _canonical_version(index_path: Path) -> str:
    versions = _find_versions(_read_text(index_path))
    if len(versions) != 1:
        msg = (
            f"{index_path} must contain exactly one canonical version tag; "
            f"found {sorted(versions) or 'none'}."
        )
        raise ValueError(msg)
    return next(iter(versions))


def _check_version_consistency(expected_tag: str) -> list[str]:
    errors: list[str] = []
    for relative_path in VERSIONED_FILES:
        full_path = DOCS_ROOT / relative_path
        versions = _find_versions(_read_text(full_path))
        if not versions:
            errors.append(f"{relative_path} does not mention {expected_tag}.")
            continue
        extra = sorted(versions - {expected_tag})
        if extra:
            errors.append(
                f"{relative_path} contains mismatched version tag(s): {', '.join(extra)} "
                f"(expected only {expected_tag})."
            )
    return errors


def _check_tiered_semantics(expected_tag: str) -> list[str]:
    if _parse_version(expected_tag) < (0, 6, 0):
        return []

    errors: list[str] = []
    configuration_text = _read_text(DOCS_ROOT / "docs/configuration.md")
    if "tiered_escalation_threshold" not in configuration_text:
        errors.append(
            "docs/configuration.md is missing tiered_escalation_threshold even though docs "
            f"claim {expected_tag} or later."
        )

    for relative_path, phrases in TIERED_STALE_PHRASES.items():
        text = _read_text(DOCS_ROOT / relative_path)
        for phrase in phrases:
            if phrase in text:
                errors.append(
                    f"{relative_path} still contains stale pre-tiered wording: {phrase!r}."
                )
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--expected-version",
        help="Expected canonical version tag (for example v0.5.1). Defaults to docs/index.md.",
    )
    args = parser.parse_args()

    try:
        expected_tag = args.expected_version or _canonical_version(DOCS_ROOT / "docs/index.md")
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1

    errors = _check_version_consistency(expected_tag)
    errors.extend(_check_tiered_semantics(expected_tag))

    if errors:
        print("Docs alignment check failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"Docs alignment is consistent for {expected_tag}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
