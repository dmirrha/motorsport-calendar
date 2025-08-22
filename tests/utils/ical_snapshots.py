"""Utilities for normalizing and comparing iCalendar (.ics) files in tests.

The goal is to make snapshot comparisons stable by removing or normalizing
volatile properties (UID, DTSTAMP, CREATED, LAST-MODIFIED, SEQUENCE, PRODID)
so tests remain deterministic across runs and machines.
"""
from __future__ import annotations

from pathlib import Path
import difflib
import re
from typing import Union


def _to_text(data: Union[str, bytes]) -> str:
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except Exception:
            return data.decode("latin-1", errors="ignore")
    return data


def normalize_ics_text(content: Union[str, bytes]) -> str:
    """Return a normalized textual representation of an ICS for snapshot testing.

    - Unify newlines to \n
    - Remove or normalize volatile fields: UID, DTSTAMP, CREATED,
      LAST-MODIFIED, SEQUENCE, PRODID
    - Trim trailing whitespace
    """
    text = _to_text(content)
    # Normalize newlines
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Unfold iCalendar folded lines (RFC 5545): a line that begins with a single space
    # is a continuation of the previous line. Join them for stable comparisons.
    unfolded_lines: list[str] = []
    for line in text.split("\n"):
        if line.startswith(" ") and unfolded_lines:
            # append continuation without the leading space
            unfolded_lines[-1] += line[1:]
        else:
            unfolded_lines.append(line)
    text = "\n".join(unfolded_lines)

    # Normalize UID lines to a fixed token (keep the property presence)
    text = re.sub(r"^UID:.*$", "UID:FIXED-UID", text, flags=re.MULTILINE)

    # Remove fields known to vary every run
    volatile_prefixes = (
        "DTSTAMP:",
        "CREATED:",
        "LAST-MODIFIED:",
        "SEQUENCE:",
        "PRODID:",
    )
    normalized_lines = []
    for line in text.split("\n"):
        if any(line.startswith(prefix) for prefix in volatile_prefixes):
            continue
        # Normalize DESCRIPTION content to avoid environment-dependent differences
        # (e.g., emoji encoded as #x1F3C1 vs literal, and wrapping/folding).
        if line.startswith("DESCRIPTION:"):
            normalized_lines.append("DESCRIPTION:__NORMALIZED__")
            continue
        # Remove trailing spaces for stability
        normalized_lines.append(line.rstrip())

    normalized = "\n".join(normalized_lines)

    # Ensure trailing newline
    if not normalized.endswith("\n"):
        normalized += "\n"

    return normalized


def compare_or_write_snapshot(generated_path: Union[str, Path], snapshot_path: Union[str, Path]) -> None:
    """Compare a generated ICS against a normalized snapshot.

    If the snapshot does not exist, create it from the normalized generated ICS
    and pass the test. Subsequent runs must match.
    """
    gen_path = Path(generated_path)
    snap_path = Path(snapshot_path)
    snap_path.parent.mkdir(parents=True, exist_ok=True)

    gen_norm = normalize_ics_text(gen_path.read_bytes())

    if not snap_path.exists():
        snap_path.write_text(gen_norm, encoding="utf-8")
        # First run: snapshot recorded.
        return

    snap_norm = normalize_ics_text(snap_path.read_text(encoding="utf-8"))

    if gen_norm != snap_norm:
        diff = "\n".join(
            difflib.unified_diff(
                snap_norm.splitlines(),
                gen_norm.splitlines(),
                fromfile=str(snap_path),
                tofile=str(gen_path),
                lineterm="",
            )
        )
        raise AssertionError(
            "ICS snapshot mismatch. Review diff and update the snapshot if intentional:\n" + diff
        )


__all__ = ["normalize_ics_text", "compare_or_write_snapshot"]
