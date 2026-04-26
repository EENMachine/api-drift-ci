"""Create or update a sticky issue comment on the current pull request."""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path


def request_json(
    method: str,
    url: str,
    token: str,
    data: dict | None = None,
) -> dict:
    body_bytes = None if data is None else json.dumps(data).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body_bytes,
        method=method,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
            **({"Content-Type": "application/json"} if body_bytes else {}),
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def main() -> None:
    marker = os.environ.get("MARKER", "<!-- api-drift-ci -->")
    repo = os.environ["GITHUB_REPOSITORY"]
    token = os.environ["GITHUB_TOKEN"]
    pr_number = int(os.environ["PR_NUMBER"])
    body = Path(sys.argv[1]).read_text(encoding="utf-8")

    owner, name = repo.split("/", 1)
    base = f"https://api.github.com/repos/{owner}/{name}"
    list_url = f"{base}/issues/{pr_number}/comments?per_page=100"

    req = urllib.request.Request(
        list_url,
        headers={
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {token}",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        comments = json.loads(resp.read().decode("utf-8"))

    existing_id = None
    for c in comments:
        if marker in (c.get("body") or ""):
            existing_id = c["id"]
            break

    payload = {"body": body}
    if existing_id is not None:
        request_json("PATCH", f"{base}/issues/comments/{existing_id}", token, payload)
        print(f"Updated comment id={existing_id}")
    else:
        out = request_json("POST", f"{base}/issues/{pr_number}/comments", token, payload)
        print(f"Created comment id={out.get('id')}")


if __name__ == "__main__":
    try:
        main()
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        print(f"GitHub API error {e.code}: {err}", file=sys.stderr)
        sys.exit(1)
