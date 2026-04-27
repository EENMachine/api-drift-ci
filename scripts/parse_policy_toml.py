"""Parse .api-drift-ci.toml / api-drift-ci.toml; emit JSON with optional ignore file paths."""
from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path


def main() -> None:
    path = Path(sys.argv[1])
    if not path.is_file():
        print("{}")
        return
    try:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except tomllib.TOMLDecodeError as e:
        print(json.dumps({"error": str(e)}))
        return

    if not isinstance(data, dict):
        print("{}")
        return

    def safe_repo_rel(p: str) -> bool:
        s = p.strip()
        if not s:
            return False
        if s.startswith(("/", "\\")):
            return False
        path = Path(s)
        if path.is_absolute():
            return False
        return ".." not in path.parts

    err = data.get("err_ignore_file")
    warn = data.get("warn_ignore_file")
    out: dict[str, str | None] = {}
    if isinstance(err, str) and err.strip():
        s = err.strip()
        if not safe_repo_rel(s):
            print(json.dumps({"error": f"Invalid err_ignore_file path: {s!r}"}))
            return
        out["err_ignore_file"] = s
    if isinstance(warn, str) and warn.strip():
        s = warn.strip()
        if not safe_repo_rel(s):
            print(json.dumps({"error": f"Invalid warn_ignore_file path: {s!r}"}))
            return
        out["warn_ignore_file"] = s
    print(json.dumps(out))


if __name__ == "__main__":
    main()
