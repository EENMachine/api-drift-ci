# Contributing

Thank you for helping improve **API Drift CI**.

## Development

- Edit the composite (`action.yml`, `run.sh`, `scripts/`) and validate with `.github/workflows/openapi-drift.yml` using `uses: ./`.
- Locally: `bash -n run.sh` and `python3 -m py_compile scripts/render_body.py scripts/post_pr_comment.py` (CI runs the same checks on Ubuntu).

## Pull requests

- Keep each PR focused on one concern.
- Update [CHANGELOG.md](CHANGELOG.md) under `[Unreleased]` when adopters would notice a behavior or docs change.
- If you change the reusable workflow’s composite pin, follow [docs/MAINTAINERS.md](docs/MAINTAINERS.md) at release time so tags stay consistent.

## Releases

Maintainers: follow the checklist in [docs/MAINTAINERS.md](docs/MAINTAINERS.md) before publishing a new `v*` tag.

## Code of conduct

All contributors agree to abide by the [Code of Conduct](CODE_OF_CONDUCT.md).
