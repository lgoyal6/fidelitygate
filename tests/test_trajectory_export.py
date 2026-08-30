from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType


def load_exporter() -> ModuleType:
    path = Path(__file__).parents[1] / "scripts" / "export_codex_trajectory.py"
    spec = importlib.util.spec_from_file_location("trajectory_exporter", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_export_excludes_instructions_and_redacts_secrets(tmp_path: Path) -> None:
    exporter = load_exporter()
    source = tmp_path / "rollout-test-thread.jsonl"
    records = [
        {
            "timestamp": "2026-01-01T00:00:00Z",
            "type": "response_item",
            "payload": {"type": "message", "role": "developer", "content": []},
        },
        {
            "timestamp": "2026-01-01T00:00:01Z",
            "type": "response_item",
            "payload": {
                "type": "message",
                "role": "user",
                "content": [{"type": "input_text", "text": "Use token=verysecretvalue"}],
            },
        },
        {
            "timestamp": "2026-01-01T00:00:02Z",
            "type": "response_item",
            "payload": {"type": "reasoning", "encrypted_content": "private"},
        },
        {
            "timestamp": "2026-01-01T00:00:03Z",
            "type": "response_item",
            "payload": {
                "type": "custom_tool_call",
                "call_id": "call-1",
                "name": "exec",
                "input": '{"cmd":"pwd"}',
            },
        },
    ]
    source.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")
    output = tmp_path / "export.jsonl"

    manifest = exporter.export_session(source, output, 20_000)
    exported = [json.loads(line) for line in output.read_text(encoding="utf-8").splitlines()]

    assert manifest["raw_record_count"] == 4
    assert manifest["exported_record_count"] == 2
    assert "verysecretvalue" not in output.read_text(encoding="utf-8")
    assert exported[0]["content"] == "Use token=[REDACTED_SECRET]"
    assert exported[1]["kind"] == "custom_tool_call"
