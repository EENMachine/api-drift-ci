# Ship and market api-drift-ci

This file is the single playbook for maintainers: what the product is, how we release it, and how we talk about it in public.

## What we are selling (in one breath)

**api-drift-ci** is a GitHub Action that compares your OpenAPI file on the **PR base** versus **PR head**, writes a **sticky PR comment** with breaking and non-breaking changes (via [oasdiff](https://github.com/oasdiff/oasdiff)), and can **fail CI** when the spec breaks clients. No hosted service is required for the core value.

## Who it is for

- Teams that already keep an OpenAPI spec in git and want **visibility on every PR** without running a separate diff tool locally.
- **Platform / API governance** engineers who want a lightweight gate: comment always, optional fail on breaking.
- **Open-source API** maintainers who want contributors to see impact of schema edits immediately.

## What “done” looks like for v1

- Composite action is stable on `ubuntu-latest`, documented inputs, predictable PR comment.
- **Semver tags** (`v0.1.0`, `v0.2.0`, …) and a **moving `v0` tag** (optional) for consumers who want floating minor updates.
- **Reusable workflow** stays in lockstep with the composite version pin (see release checklist).
- README answers: install in 60 seconds, fork PR safety, permissions, troubleshooting.

## How we ship (technical)

### Repositories and refs

- **Default branch:** `master` (this repo). Consumers may pin `uses: EENMachine/api-drift-ci@v0.1.0` or `@master` during evaluation only.
- **Artifacts:** `action.yml` (composite), `run.sh`, `scripts/*.py`, optional `.github/workflows/reusable-openapi-drift.yml`.

### Release checklist (every tag)

1. Update **CHANGELOG.md** with a dated section for the new version.
2. In **`.github/workflows/reusable-openapi-drift.yml`**, set the composite `uses:` line to the **same tag** you are about to create (e.g. `EENMachine/api-drift-ci@v0.2.0`). This keeps reusable workflows reproducible.
3. Commit on `master` with message `Release vX.Y.Z`.
4. Tag: `git tag vX.Y.Z` on that commit (annotated tag optional).
5. Push: `git push origin master && git push origin vX.Y.Z`.
6. On GitHub: confirm **Actions** pass on `master`; spot-check a PR in a sandbox repo using the new tag.

### GitHub Marketplace (optional later)

- Requirements: good README, branding in `action.yml`, clear description, MIT license, categories “API management” / “Continuous integration”.
- [Publishing guide](https://docs.github.com/en/actions/creating-actions/publishing-actions-in-github-marketplace).
- After listing, add a Marketplace badge to the README.

### Version policy

- **v0.x:** breaking changes to inputs or behavior allowed; document in CHANGELOG.
- **v1.0:** commit to stable inputs and comment shape; deprecate before removal.

## How we market (simple and repeatable)

### Core message (copy anywhere)

> Stop shipping silent API breaks. api-drift-ci comments every pull request with OpenAPI breaking vs safe changes—powered by oasdiff—and can fail the build when clients would break.

### Channels (in order of effort vs reach)

1. **README + repo presentation** — Clear hero sentence, screenshot or sample comment, two-line install. Set GitHub **About** description and **Topics** (suggested): `openapi`, `openapi3`, `github-actions`, `api`, `ci`, `continuous-integration`, `swagger`, `pull-request`, `developer-experience`.
2. **Show HN / dev communities** — Short post: problem, link, one screenshot of PR comment.
3. **Changelog / newsletter** — Submit to weekly dev newsletters if you maintain a personal blog post linking here.
4. **Talks / lunch-and-learns** — Five-minute internal demo: “before/after PR comment.”

### What we are not claiming

- We do not replace full design-first governance tools; we **diff what is in git** on the PR timeline.
- We are not a hosted registry; we integrate with **GitHub PRs** first.

### Optional monetization paths (later, not required for OSS)

- **Support contract** or setup help for enterprises (same codebase, paid SLA).
- **Hosted** diff-as-a-service only if demand appears; keep the Action as the free wedge.

## Support stance

- **Issues** on GitHub for bugs and feature ideas.
- **SECURITY.md** for vulnerability reports.

## Success metrics (lightweight)

- GitHub **Stars** and **Dependents** graph (who pins the action).
- Occasional **issues/PRs** from non-maintainers (signal of adoption).
- Internal: number of repos in your org using the reusable workflow.
