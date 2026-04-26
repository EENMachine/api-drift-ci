"""Append a rich Job Summary (GitHub Actions) for API Drift CI."""
from __future__ import annotations

import json
import os
from pathlib import Path


def main() -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if not summary_path:
        return

    spec = os.environ.get("SPEC_PATH", "")
    base = os.environ.get("BASE_SHA", "")[:7]
    head = os.environ.get("HEAD_SHA", "")[:7]
    pr_url = os.environ.get("PR_HTML_URL", "").strip()
    breaking_exit = int(os.environ.get("BREAKING_EXIT_CODE", "0"))
    fail_on = os.environ.get("FAIL_ON_BREAKING", "true").lower() == "true"
    policy_note = os.environ.get("POLICY_NOTE", "").strip()

    breaking_path = Path(os.environ.get("BREAKING_MD_PATH", ""))
    breaking_excerpt = ""
    if breaking_path.is_file():
        raw = breaking_path.read_text(encoding="utf-8").strip()
        lines = raw.splitlines()
        breaking_excerpt = "\n".join(lines[:36])
        if len(lines) > 36:
            breaking_excerpt += "\n\n_(Truncated for summary; see PR comment for full output.)_"

    summary_json_path = Path(os.environ.get("SUMMARY_JSON_PATH", ""))
    summary_hint = ""
    if summary_json_path.is_file():
        try:
            s = json.loads(summary_json_path.read_text(encoding="utf-8"))
            if s.get("diff") is True and isinstance(s.get("details"), dict):
                summary_hint = f"```json\n{json.dumps(s['details'], indent=2)[:800]}\n```\n"
        except (json.JSONDecodeError, OSError, TypeError):
            pass

    job_fails = fail_on and breaking_exit != 0
    if breaking_exit != 0:
        verdict = "Breaking changes reported by **oasdiff** (ERR)."
        result_label = "**Result: attention required**"
    else:
        verdict = "No ERR-level breaking changes reported by **oasdiff** for this diff."
        result_label = "**Result: OK**"

    lines: list[str] = [
        "## API Drift CI — job summary",
        "",
        result_label,
        "",
        verdict,
        "",
        "| | |",
        "| --- | --- |",
        f"| **Spec** | `{spec}` |",
        f"| **Base → head** | `{base}` → `{head}` |",
        f"| **Fail on breaking** | `{'true' if fail_on else 'false'}` |",
        f"| **oasdiff exit** (with `--fail-on ERR`) | `{breaking_exit}` |",
        f"| **This job** | **{'failed' if job_fails else 'passed'}** |",
        "",
    ]
    if policy_note:
        lines += ["### Policy", "", policy_note, ""]
    if pr_url:
        lines += ["### Pull request", "", f"[Open pull request]({pr_url})", ""]
    lines += [
        "### oasdiff summary (details)",
        "",
        summary_hint if summary_hint else "_No structured summary available._",
        "",
        "### Breaking output (excerpt)",
        "",
        "<details><summary>Expand</summary>",
        "",
        breaking_excerpt if breaking_excerpt else "_None._",
        "",
        "</details>",
        "",
        "---",
        "_Sticky PR comment was updated in this run (see the PR **Conversation** tab)._",
        "",
    ]

    with Path(summary_path).open("a", encoding="utf-8") as fh:
        fh.write("\n".join(lines))


if __name__ == "__main__":
    main()
