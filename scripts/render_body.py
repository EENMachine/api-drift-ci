"""Build markdown PR comment from oasdiff artifacts."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path


def main() -> None:
    marker = os.environ.get("MARKER", "<!-- api-drift-ci -->")
    title = os.environ.get("COMMENT_TITLE", "OpenAPI drift")
    base_mode = os.environ.get("BASE_MODE", "file")
    max_ch = int(os.environ.get("MAX_CHANGELOG_CHARS", "14000"))
    spec = os.environ["SPEC_PATH"]
    base_sha = os.environ["BASE_SHA"][:7]
    head_sha = os.environ["HEAD_SHA"][:7]

    summary_path = Path(os.environ["SUMMARY_JSON"])
    breaking_path = Path(os.environ["BREAKING_MD"])
    changelog_path = Path(os.environ["CHANGELOG_MD"])

    summary = json.loads(summary_path.read_text(encoding="utf-8"))
    breaking_md = breaking_path.read_text(encoding="utf-8").strip()
    changelog_md = changelog_path.read_text(encoding="utf-8").strip()

    details = summary.get("details") if isinstance(summary.get("details"), dict) else {}
    endpoints = details.get("endpoints", {}) if isinstance(details.get("endpoints"), dict) else {}
    paths = details.get("paths", {}) if isinstance(details.get("paths"), dict) else {}

    ep_parts = []
    for key in ("added", "deleted", "modified", "deprecated"):
        if key in endpoints and endpoints[key]:
            ep_parts.append(f"{key} **{endpoints[key]}**")
    path_parts = []
    for key in ("added", "deleted", "modified", "deprecated"):
        if key in paths and paths[key]:
            path_parts.append(f"{key} **{paths[key]}**")

    summary_line = []
    if summary.get("diff") is False:
        summary_line.append("No structural diff reported (specs may still differ in non-compared ways).")
    else:
        if ep_parts:
            summary_line.append("Endpoints: " + ", ".join(ep_parts) + ".")
        if path_parts:
            summary_line.append("Paths: " + ", ".join(path_parts) + ".")
        if not summary_line:
            summary_line.append("Changes detected; see changelog below.")

    if len(changelog_md) > max_ch:
        changelog_md = changelog_md[:max_ch] + "\n\n_(Changelog truncated.)_"

    lines: list[str] = [
        marker,
        f"## {title}",
        "",
        f"**Spec:** `{spec}`  ",
        f"**Base:** `{base_sha}` → **Head:** `{head_sha}`",
    ]
    if base_mode == "missing-on-base":
        lines += [
            "",
            "_Base revision had no file at this path; compared head against an empty OpenAPI stub "
            "(additive-only interpretation)._",
        ]
    lines += ["", "### Summary", "", "\n".join(summary_line), "", "### Breaking changes"]
    lines += [breaking_md if breaking_md else "_None detected._", "", "### Full changelog"]
    lines += [changelog_md if changelog_md else "_No changes._", "", "---"]
    prod = os.environ.get("PRODUCT_REPOSITORY", "").strip()
    if prod and "/" in prod:
        url = f"https://github.com/{prod}"
        lines.append(f"_Posted by [**api-drift-ci**]({url}). Powered by [oasdiff](https://github.com/oasdiff/oasdiff)._")
    else:
        lines.append("_Posted by **api-drift-ci** (powered by [oasdiff](https://github.com/oasdiff/oasdiff))._")
    sys.stdout.write("\n".join(lines))


if __name__ == "__main__":
    main()
