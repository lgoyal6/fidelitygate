#!/usr/bin/env python3
"""Export a redacted, judge-readable subset of a Codex JSONL session."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from collections import Counter
from pathlib import Path
from typing import Any

ALLOWED_ITEM_TYPES = {
    "custom_tool_call",
    "custom_tool_call_output",
    "function_call",
    "function_call_output",
}
SECRET_PATTERNS = (
    (re.compile(r"\bsk-[A-Za-z0-9_-]{16,}\b"), "[REDACTED_OPENAI_KEY]"),
    (re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"), "[REDACTED_GITHUB_TOKEN]"),
    (
        re.compile(r"(?i)(authorization\s*:\s*bearer\s+)[^\s\"']+"),
        r"\1[REDACTED_BEARER_TOKEN]",
    ),
    (
        re.compile(
            r"(?i)(\b(?:api[_-]?key|token|secret|password)\b\s*[=:]\s*)"
            r"([\"']?)[^\s,;\"']{8,}\2"
        ),
        r"\1[REDACTED_SECRET]",
    ),
    (
        re.compile(r"(?i)(one-time code[^A-Z0-9]*)([A-Z0-9]{4}-[A-Z0-9]{4})"),
        r"\1[REDACTED_DEVICE_CODE]",
    ),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--input", type=Path, help="Explicit Codex rollout JSONL file")
    source.add_argument("--thread-id", help="Thread ID used to locate the rollout below CODEX_HOME")
    parser.add_argument("--output", type=Path, required=True, help="Destination sanitized JSONL")
    parser.add_argument(
        "--max-field-chars",
        type=int,
        default=20_000,
        help="Maximum characters retained in any individual text field",
    )
    parser.add_argument(
        "--ordinal-range",
        action="append",
        default=[],
        metavar="START:END",
        help="Include an inclusive raw-record ordinal range; repeat for multiple stages",
    )
    return parser.parse_args()


def parse_ordinal_ranges(values: list[str]) -> list[tuple[int, int]]:
    ranges: list[tuple[int, int]] = []
    for value in values:
        try:
            start_text, end_text = value.split(":", maxsplit=1)
            start, end = int(start_text), int(end_text)
        except (ValueError, TypeError) as error:
            raise ValueError(f"invalid ordinal range {value!r}; expected START:END") from error
        if start < 0 or end < start:
            raise ValueError(f"invalid ordinal range {value!r}; require 0 <= START <= END")
        ranges.append((start, end))
    return ranges


def ordinal_selected(ordinal: int, ranges: list[tuple[int, int]]) -> bool:
    return not ranges or any(start <= ordinal <= end for start, end in ranges)


def codex_home() -> Path:
    configured = os.environ.get("CODEX_HOME")
    return Path(configured).expanduser() if configured else Path.home() / ".codex"


def locate_session(thread_id: str) -> Path:
    matches = sorted((codex_home() / "sessions").rglob(f"*{thread_id}*.jsonl"))
    if not matches:
        raise FileNotFoundError(f"no Codex session found for thread ID {thread_id}")
    if len(matches) > 1:
        paths = "\n".join(str(path) for path in matches)
        raise RuntimeError(f"multiple sessions matched thread ID {thread_id}:\n{paths}")
    return matches[0]


def redact_text(value: str, max_chars: int) -> str:
    """Apply conservative token redaction, home-path minimization, and length bounds."""
    redacted = value.replace(str(Path.home()), "$HOME")
    for pattern, replacement in SECRET_PATTERNS:
        redacted = pattern.sub(replacement, redacted)
    if len(redacted) > max_chars:
        omitted = len(redacted) - max_chars
        redacted = f"{redacted[:max_chars]}\n[TRUNCATED {omitted} CHARACTERS]"
    return redacted


def redact_value(value: Any, max_chars: int) -> Any:
    if isinstance(value, str):
        return redact_text(value, max_chars)
    if isinstance(value, list):
        return [redact_value(item, max_chars) for item in value]
    if isinstance(value, dict):
        return {
            str(key): redact_value(item, max_chars)
            for key, item in value.items()
            if key not in {"encrypted_content", "internal_chat_message_metadata_passthrough"}
        }
    return value


def message_text(payload: dict[str, Any]) -> str:
    fragments: list[str] = []
    for item in payload.get("content", []):
        if not isinstance(item, dict):
            continue
        text = item.get("text")
        if isinstance(text, str):
            fragments.append(text)
    return "\n".join(fragments)


def export_record(record: dict[str, Any], max_chars: int) -> dict[str, Any] | None:
    """Reduce one raw record to the audit-relevant public schema."""
    if record.get("type") != "response_item" or not isinstance(record.get("payload"), dict):
        return None
    payload: dict[str, Any] = record["payload"]
    item_type = payload.get("type")
    timestamp = record.get("timestamp")
    ordinal = record.get("ordinal")

    if item_type == "message":
        role = payload.get("role")
        if role not in {"user", "assistant"}:
            return None
        content = message_text(payload)
        if role == "user" and content.lstrip().startswith("<environment_context>"):
            return None
        return {
            "timestamp": timestamp,
            "ordinal": ordinal,
            "kind": "message",
            "role": role,
            "content": redact_text(content, max_chars),
        }

    if item_type not in ALLOWED_ITEM_TYPES:
        return None
    exported: dict[str, Any] = {
        "timestamp": timestamp,
        "ordinal": ordinal,
        "kind": item_type,
        "call_id": payload.get("call_id"),
    }
    if "name" in payload:
        exported["name"] = payload.get("name")
    for field in ("arguments", "input", "output"):
        if field in payload:
            exported[field] = redact_value(payload[field], max_chars)
    return exported


def export_session(
    source: Path,
    output: Path,
    max_chars: int,
    ordinal_ranges: list[tuple[int, int]] | None = None,
) -> dict[str, Any]:
    """Validate raw JSONL, export selected records, and return an audit manifest."""
    raw = source.read_bytes()
    records: list[dict[str, Any]] = []
    raw_count = 0
    selected_raw_count = 0
    selected_ranges = ordinal_ranges or []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        raw_count += 1
        try:
            value = json.loads(line)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON on line {line_number}: {error}") from error
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number} is not a JSON object")
        ordinal_value = value.get("ordinal", line_number - 1)
        if not isinstance(ordinal_value, int):
            raise ValueError(f"line {line_number} has a non-integer ordinal")
        if not ordinal_selected(ordinal_value, selected_ranges):
            continue
        selected_raw_count += 1
        exported = export_record(value, max_chars)
        if exported is not None:
            records.append(exported)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "".join(json.dumps(record, sort_keys=True) + "\n" for record in records),
        encoding="utf-8",
    )
    counts = Counter(str(record["kind"]) for record in records)
    manifest = {
        "schema_version": "1",
        "source_filename": source.name,
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "raw_record_count": raw_count,
        "selected_raw_record_count": selected_raw_count,
        "exported_record_count": len(records),
        "exported_kind_counts": dict(sorted(counts.items())),
        "output_sha256": hashlib.sha256(output.read_bytes()).hexdigest(),
        "policy": {
            "included": "user/assistant messages and tool calls/responses",
            "excluded": "system/developer messages, internal reasoning, and runtime metadata",
            "home_paths_minimized": True,
            "credential_patterns_redacted": True,
            "max_field_chars": max_chars,
            "ordinal_ranges": [f"{start}:{end}" for start, end in selected_ranges],
            "manual_review_required_before_commit": True,
        },
    }
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return manifest


def main() -> None:
    args = parse_args()
    source = args.input if args.input is not None else locate_session(args.thread_id)
    ranges = parse_ordinal_ranges(args.ordinal_range)
    manifest = export_session(source.resolve(), args.output.resolve(), args.max_field_chars, ranges)
    print(
        f"Exported {manifest['exported_record_count']} of {manifest['raw_record_count']} "
        f"records to {args.output}"
    )


if __name__ == "__main__":
    main()
