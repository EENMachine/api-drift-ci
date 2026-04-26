# Maintainer handbook

Internal playbook for releases, GitHub Marketplace, and positioning. **Customers** should start with the [README](../README.md); use this file when you ship new versions or list the action.

## Release checklist (every version tag)

1. Update [CHANGELOG.md](../CHANGELOG.md): move items from `[Unreleased]` into a dated `## [X.Y.Z]` section.
2. In [`.github/workflows/reusable-openapi-drift.yml`](../.github/workflows/reusable-openapi-drift.yml), set the composite `uses: EENMachine/api-drift-ci@…` pin to the **same tag** you are about to publish (keeps reusable workflows reproducible).
3. In [README.md](../README.md), update example pins (`@vX.Y.Z`) to match.
4. Commit on `master` with message `Release vX.Y.Z`.
5. Tag: `git tag -a vX.Y.Z -m "vX.Y.Z"` (annotated recommended).
6. Push: `git push origin master && git push origin vX.Y.Z`.
7. On GitHub: confirm Actions are green; open a test PR in a sandbox repo using the new tag.

## GitHub Marketplace

### Before you click “Publish”

- [ ] [README](../README.md) has a clear customer path (install, permissions, troubleshooting links).
- [ ] [action.yml](../action.yml): `name` ≤ 34 characters, `description` ≤ 125 characters, `branding` set, MIT [LICENSE](../LICENSE) present.
- [ ] [SECURITY.md](../SECURITY.md) explains reporting and fork/token considerations.
- [ ] [CODE_OF_CONDUCT.md](../CODE_OF_CONDUCT.md) and [CONTRIBUTING.md](../CONTRIBUTING.md) are in place.
- [ ] Repo **About** description and **Topics** filled in (copy from [docs/REPO_SETTINGS.md](REPO_SETTINGS.md)).

### Publish flow

1. Open the repository on GitHub → **Actions** → select **API Drift CI** (or the action metadata) → follow [Publishing actions to the Marketplace](https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace).
2. Choose categories that match buyer intent (for example **API management**, **Continuous integration**).
3. After approval, add a Marketplace badge to the README (snippet in [REPO_SETTINGS.md](REPO_SETTINGS.md)).

### Version policy

- **v0.x:** breaking changes to inputs or comment layout allowed; document in CHANGELOG.
- **v1.0:** commit to stable inputs and comment shape; deprecate before removal.

## Positioning and copy

### Shipped differentiators (keep these sharp in marketing)

- **Actions job summary** — every run writes to `$GITHUB_STEP_SUMMARY` so CI consumers see a verdict without opening the PR.
- **Repo policy (`.api-drift-ci.toml`)** — maps to oasdiff’s native `--err-ignore` / `--warn-ignore` files; no parallel ignore grammar to learn beyond oasdiff’s own format ([docs/POLICY_FILE.md](POLICY_FILE.md)).

### One-line pitch

> Stop shipping silent API breaks: every pull request gets a sticky OpenAPI diff (breaking vs safe) and optional CI failure—powered by oasdiff.

### Who it is for

- Teams with an OpenAPI spec in git who want **visibility on every PR** without a separate diff tool.
- Platform or API owners who want **comment always**, **fail only on breaking**.
- Open-source APIs that want contributors to see schema impact immediately.

### What we do not claim

- We do not replace full API design platforms; we **diff what is committed** on the PR timeline.
- We are not a registry product; we integrate with **GitHub pull requests** first.

### Suggested outreach channels

1. Set repo **About** + **Topics** (see [REPO_SETTINGS.md](REPO_SETTINGS.md)).
2. Short demo post (Show HN, Reddit, etc.) with one screenshot of a PR comment.
3. Internal lunch-and-learn: before/after in five minutes.

## Support stance

- **Issues:** bugs and feature ideas (use templates in `.github/ISSUE_TEMPLATE`).
- **Security:** [SECURITY.md](../SECURITY.md) and private GitHub advisories.

## Success signals

- Dependents graph and pins on `uses: EENMachine/api-drift-ci@v…`.
- Issues or PRs from outside the core maintainers.
