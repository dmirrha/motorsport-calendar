"""Utilities for safe Markdown front matter handling.

Rules:
- Only treat YAML front matter when the very first line is exactly '---'.
- Front matter ends at the next line that is exactly '---'.
- On malformed YAML or missing closing fence, fall back to returning the original content.

This avoids crashes when '---' appears in the middle of a Markdown file as a horizontal rule.
"""
from __future__ import annotations

from typing import Tuple, Optional, Dict, Any

import yaml


def split_front_matter(md_text: str) -> tuple[Optional[Dict[str, Any]], str]:
    """Split Markdown text into (front_matter, content).

    Front matter is parsed with yaml.safe_load ONLY if the first line is '---'
    and a closing '---' exists. If YAML parsing fails or the closing fence is
    missing, returns (None, original_text).
    """
    if not md_text:
        return None, md_text

    lines = md_text.splitlines()
    if not lines:
        return None, md_text

    if lines[0].strip() != '---':
        # Not a front matter: return original
        return None, md_text

    # Find closing fence
    end_idx: Optional[int] = None
    for i in range(1, len(lines)):
        if lines[i].strip() == '---':
            end_idx = i
            break

    if end_idx is None:
        # Missing closing fence: fall back to original
        return None, md_text

    yaml_payload = '\n'.join(lines[1:end_idx])
    content = '\n'.join(lines[end_idx + 1 :])

    try:
        meta = yaml.safe_load(yaml_payload) or {}
        if not isinstance(meta, dict):
            # Non-dict front matter is unusual; still accept but normalize to dict
            meta = {"_front_matter": meta}
        return meta, content
    except Exception:
        # YAML parsing failed: fall back to original
        return None, md_text


def strip_front_matter(md_text: str) -> str:
    """Return Markdown content without front matter, if present at the top.

    If no valid front matter is found, returns the original text unchanged.
    """
    _, content = split_front_matter(md_text)
    return content
