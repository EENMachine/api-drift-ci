# api-drift-ci

[![CI](https://github.com/EENMachine/api-drift-ci/actions/workflows/ci.yml/badge.svg)](https://github.com/EENMachine/api-drift-ci/actions/workflows/ci.yml)

**OpenAPI drift checks for every pull request.** This GitHub Action compares your spec at the **PR base SHA** and **PR head SHA**, posts a **sticky PR comment** (markdown from [oasdiff](https://github.com/oasdiff/oasdiff)), and can **fail the job** when breaking changes are detected. Runs on **`ubuntu-latest`** (downloads the Linux `oasdiff` binary).

| If you want… | Read this first |
| --- | --- |
| To adopt it in your repo in under a minute | [Quick start](#quick-start) |
| A one-job wrapper you reuse across many services | [Reusable workflow](#reusable-workflow) |
| How we tag, release, and talk about the product | [**docs/SHIP_AND_MARKET.md**](docs/SHIP_AND_MARKET.md) |
| Fork PRs and `$ref` safety | [**SECURITY.md**](SECURITY.md) |

---

## Quick start

**Requirements:** `ubuntu-latest`, `actions/checkout@v4` with **`fetch-depth: 0`**, and `pull-requests: write` on the token.

```yaml
name: OpenAPI drift

on:
  pull_request:
    paths:
      - "docs/openapi.yaml" # change to your spec path

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

      - uses: EENMachine/api-drift-ci@v0.1.0
        with:
          spec-path: docs/openapi.yaml
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

`fetch-depth: 0` is required so `git show <sha>:path` can read both sides of the PR.

---

## Reusable workflow

In each service repo, call the workflow we publish here (pin the **`@v…`** ref you trust):

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
    uses: EENMachine/api-drift-ci/.github/workflows/reusable-openapi-drift.yml@v0.1.0
    with:
      spec-path: docs/openapi.yaml
```

Optional `with:` keys match the composite inputs (`fail-on-breaking`, `oasdiff-version`, `comment-title`, `max-changelog-chars`, `allow-external-refs`). The reusable workflow’s internal composite pin is bumped **on each release** so the tag stays self-consistent (see [docs/SHIP_AND_MARKET.md](docs/SHIP_AND_MARKET.md)).

---

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `spec-path` | yes | — | Repo-relative path to the OpenAPI file on base and head. |
| `github-token` | yes | — | Typically `secrets.GITHUB_TOKEN` (needs `pull-requests: write`). |
| `oasdiff-version` | no | `1.15.0` | oasdiff release (no `v` prefix). |
| `fail-on-breaking` | no | `true` | Fail the job when `oasdiff breaking --fail-on ERR` exits non-zero. |
| `comment-title` | no | `OpenAPI drift` | PR comment heading. |
| `max-changelog-chars` | no | `14000` | Truncate changelog section in the comment. |
| `allow-external-refs` | no | `true` | When `false`, passes `--allow-external-refs=false` to oasdiff (stricter for untrusted fork PRs; may break specs that use external `$ref`). |

---

## Behavior

- Runs on **`pull_request`** only (other events log and exit successfully).
- If the spec is **missing on the base** commit, head is compared to a tiny empty OpenAPI stub (useful when you **add** a spec file in a PR).
- The PR comment contains a hidden HTML marker so the same comment is **updated** on new pushes.
- Breaking vs non-breaking rules are entirely those of **oasdiff** (we do not reinterpret).

---

## Project layout

| Path | Purpose |
| --- | --- |
| `action.yml` | Composite action metadata and inputs. |
| `run.sh` | Checkout-independent diff + install oasdiff + invoke scripts. |
| `scripts/render_body.py` | Build markdown for the PR comment. |
| `scripts/post_pr_comment.py` | Upsert the sticky comment via the GitHub API. |
| `.github/workflows/reusable-openapi-drift.yml` | Caller-friendly `workflow_call` wrapper. |
| `docs/SHIP_AND_MARKET.md` | **Shipping and marketing playbook** for maintainers. |

---

## Contributing and changelog

See [**CONTRIBUTING.md**](CONTRIBUTING.md) and [**CHANGELOG.md**](CHANGELOG.md).
