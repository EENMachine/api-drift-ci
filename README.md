# api-drift-ci

Composite GitHub Action that diffs an OpenAPI document between the **pull request base SHA** and **head SHA**, posts a **sticky PR comment** (markdown from [oasdiff](https://github.com/oasdiff/oasdiff)), and optionally **fails the job** when breaking changes are reported.

**Runtime:** `ubuntu-latest` (downloads the Linux `oasdiff` binary).

## Quick start

Add a workflow (minimum):

```yaml
name: OpenAPI drift

on:
  pull_request:
    paths:
      - "docs/openapi.yaml" # adjust

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

      - uses: YOUR_ORG/api-drift-ci@v1
        with:
          spec-path: docs/openapi.yaml
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

`fetch-depth: 0` is required so `git show <sha>:path` can read both ends of the PR.

## Inputs

| Input | Required | Default | Description |
| --- | --- | --- | --- |
| `spec-path` | yes | — | Repo-relative path to the OpenAPI file on both base and head. |
| `github-token` | yes | — | Use `secrets.GITHUB_TOKEN` (needs `pull-requests: write`). |
| `oasdiff-version` | no | `1.15.0` | oasdiff release (no `v` prefix). |
| `fail-on-breaking` | no | `true` | If `true`, fail when `oasdiff breaking --fail-on ERR` exits non-zero. |
| `comment-title` | no | `OpenAPI drift` | PR comment heading. |
| `max-changelog-chars` | no | `14000` | Truncate changelog section in the comment. |

## Behavior

- Only runs on `pull_request` (other events no-op with a log line).
- If the spec is missing on the base commit, the action compares head against a tiny empty OpenAPI stub (useful when introducing a new spec file).
- The PR comment includes a hidden marker so the same comment is **updated** on new pushes.
- Breaking classification follows **oasdiff** rules (not a second opinion).

## Publishing

1. Push this repository to GitHub.
2. Tag releases (`v1`, `v1.0.0`) so consumers can pin `uses: org/api-drift-ci@v1`.
3. Optionally publish to the [GitHub Marketplace](https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace) after branding and docs review.

## Product next steps

- Hosted service (upload specs, Slack/email) for teams not on GitHub.
- Optional GraphQL SDL support.
- `workflow_call` reusable workflow wrapper for copy-paste-free adoption.
