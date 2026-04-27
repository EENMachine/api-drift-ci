"""Lightweight tests for policy parsing and job summary (no pytest dependency)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run_parse(policy_text: str) -> dict:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".toml",
        delete=False,
        encoding="utf-8",
    ) as f:
        f.write(policy_text)
        name = f.name
    try:
        out = subprocess.check_output(
            [sys.executable, str(ROOT / "scripts" / "parse_policy_toml.py"), name],
            text=True,
        )
        return json.loads(out.strip() or "{}")
    finally:
        Path(name).unlink(missing_ok=True)


def test_parse_valid() -> None:
    data = run_parse('err_ignore_file = ".github/x.txt"\n')
    assert data.get("err_ignore_file") == ".github/x.txt"
    assert "warn_ignore_file" not in data or data.get("warn_ignore_file") is None


def test_parse_rejects_parent_dir() -> None:
    data = run_parse('err_ignore_file = "../etc/passwd"\n')
    assert "error" in data


def test_parse_rejects_absolute() -> None:
    data = run_parse('err_ignore_file = "/tmp/x"\n')
    assert "error" in data


def test_write_step_summary_smoke() -> None:
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".md",
        delete=False,
        encoding="utf-8",
    ) as br:
        br.write("## line one\nline two\n")
        br_path = br.name
    with tempfile.NamedTemporaryFile(
        mode="w",
        suffix=".json",
        delete=False,
        encoding="utf-8",
    ) as sj:
        sj.write('{"diff": true, "details": {"endpoints": {"modified": 1}}}')
        sj_path = sj.name
    out_path = Path(tempfile.mkdtemp()) / "summary.md"
    try:
        env = os.environ.copy()
        env["GITHUB_STEP_SUMMARY"] = str(out_path)
        env["SPEC_PATH"] = "docs/openapi.yaml"
        env["BASE_SHA"] = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
        env["HEAD_SHA"] = "bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb"
        env["PR_HTML_URL"] = "https://github.com/org/repo/pull/1"
        env["BREAKING_EXIT_CODE"] = "0"
        env["FAIL_ON_BREAKING"] = "true"
        env["POLICY_NOTE"] = "Loaded **.api-drift-ci.toml**."
        env["BREAKING_MD_PATH"] = br_path
        env["SUMMARY_JSON_PATH"] = sj_path
        subprocess.check_call(
            [sys.executable, str(ROOT / "scripts" / "write_step_summary.py")],
            env=env,
        )
        text = out_path.read_text(encoding="utf-8")
        assert "API Drift CI" in text
        assert "docs/openapi.yaml" in text
        assert "Result: OK" in text
    finally:
        Path(br_path).unlink(missing_ok=True)
        Path(sj_path).unlink(missing_ok=True)
        out_path.unlink(missing_ok=True)
        out_path.parent.rmdir()


def main() -> None:
    test_parse_valid()
    test_parse_rejects_parent_dir()
    test_parse_rejects_absolute()
    test_write_step_summary_smoke()
    print("ok: test_policy_and_summary")


if __name__ == "__main__":
    main()
