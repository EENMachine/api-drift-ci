# API Drift CI

**OpenAPI drift checks on every pull request** — diff your spec at the PR **base** and **head**, get one **sticky PR comment** (breaking changes + full changelog via [oasdiff](https://github.com/oasdiff/oasdiff)), and optionally **fail CI** when clients would break.

[![CI](https://github.com/EENMachine/api-drift-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/EENMachine/api-drift-ci/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/EENMachine/api-drift-ci/blob/master/LICENSE)
[![Release](https://img.shields.io/github/v/release/EENMachine/api-drift-ci?sort=semver)](https://github.com/EENMachine/api-drift-ci/releases)

---

## Why teams use this

| Benefit | What you get |
| --- | --- |
| **Visibility** | Every PR shows exactly how the published OpenAPI contract moved. |
| **Governance** | Turn on **fail on breaking** when you are ready to gate merges. |
| **Low friction** | No separate SaaS: runs in GitHub Actions on `ubuntu-latest`. |

**Runtime:** `ubuntu-latest` only (Linux **amd64** [oasdiff](https://github.com/oasdiff/oasdiff) binary).

---

## Quick start (composite action)

**Checklist:** `ubuntu-latest` · `actions/checkout@v4` with **`fetch-depth: 0`** · workflow `permissions` include **`pull-requests: write`**.

```yaml
name: OpenAPI drift

on:
  pull_request:
    paths:
      - "docs/openapi.yaml" # your spec path

permissions:
  contents: read
  pull-requests: write

jobs:
  drift:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with:
          fetch-depth: 0

      - uses: EENMachine/api-drift-ci@v0.1.1
        with:
          spec-path: docs/openapi.yaml
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

`fetch-depth: 0` is **required** so `git show <sha>:path` can read both sides of the pull request.

---

## Reusable workflow (one job per repo)

Pin the **`@v…`** ref you trust (same as the composite):

```yaml
name: OpenAPI drift

on:
  pull_request:
    paths:
      - "docs/openapi.yaml"

permissions:
  contents: read
  pull-requests: write

jobs:
  drift:
    uses: EENMachine/api-drift-ci/.github/workflows/reusable-openapi-drift.yml@v0.1.1
    with:
      spec-path: docs/openapi.yaml
```

Optional `with:` keys: `fail-on-breaking`, `oasdiff-version`, `comment-title`, `max-changelog-chars`, `allow-external-refs` (same semantics as the table below).

---

## Example output

See [**docs/EXAMPLE_PR_COMMENT.md**](docs/EXAMPLE_PR_COMMENT.md) for what the sticky PR comment looks like.

---

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `spec-path` | yes | — | Repo-relative path to the OpenAPI file on **base** and **head**. |
| `github-token` | yes | — | `secrets.GITHUB_TOKEN` or `github.token` (needs **`pull-requests: write`**). |
| `oasdiff-version` | no | `1.15.0` | oasdiff release (no `v` prefix). |
| `fail-on-breaking` | no | `true` | Fail the job when `oasdiff breaking --fail-on ERR` exits non-zero. |
| `comment-title` | no | `OpenAPI drift` | Markdown heading in the PR comment. |
| `max-changelog-chars` | no | `14000` | Truncate changelog section for very large specs. |
| `allow-external-refs` | no | `true` | Set **`false`** on untrusted fork PRs to disable remote `$ref` resolution ([**SECURITY.md**](SECURITY.md)). |

---

## Behavior (customer view)

- **Event:** `pull_request` only — other events are skipped with a log line (success).
- **New spec file:** if the file is missing on the **base** commit, the action compares **head** against a minimal empty OpenAPI stub so additive PRs still get a useful comment.
- **Sticky comment:** a hidden marker in the comment body lets the action **update** the same comment on new pushes.
- **Breaking rules:** defined by **oasdiff**, not re-interpreted here.

---

## Troubleshooting

Start with [**docs/FAQ.md**](docs/FAQ.md) (checkout depth, fork PRs, permissions, runner OS).

---

## Security

See [**SECURITY.md**](SECURITY.md) (`GITHUB_TOKEN`, fork PRs, external `$ref`).

---

## Community

- [**Contributing**](CONTRIBUTING.md)
- [**Code of Conduct**](CODE_OF_CONDUCT.md)
- [**Changelog**](CHANGELOG.md)
- [**Report an issue**](https://github.com/EENMachine/api-drift-ci/issues/new/choose)

---

## Repository layout (reference)

| Path | Role |
| --- | --- |
| `action.yml` | Composite Action metadata (also used for GitHub Marketplace). |
| `run.sh` | Installs oasdiff, runs diffs, drives scripts. |
| `scripts/render_body.py` | Builds PR markdown. |
| `scripts/post_pr_comment.py` | Creates or updates the PR comment. |
| `.github/workflows/reusable-openapi-drift.yml` | Optional `workflow_call` wrapper for adopters. |

---

## Maintainers

Publishing, Marketplace, and positioning: [**docs/MAINTAINERS.md**](docs/MAINTAINERS.md) · GitHub **About** copy: [**docs/REPO_SETTINGS.md**](docs/REPO_SETTINGS.md)

---

## License

MIT — see [**LICENSE**](LICENSE).
