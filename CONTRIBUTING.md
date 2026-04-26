# Contributing

Thanks for helping improve api-drift-ci.

## Development

- Change the composite (`action.yml`, `run.sh`, `scripts/`) and dogfood with `.github/workflows/openapi-drift.yml` (`uses: ./`).
- Run locally: `bash -n run.sh` and `python3 -m py_compile scripts/render_body.py scripts/post_pr_comment.py` (or rely on CI).

## Pull requests

- Keep the diff focused on one concern.
- Update **CHANGELOG.md** under `[Unreleased]` when the change affects users.
- If you change the reusable workflow’s composite pin, follow **docs/SHIP_AND_MARKET.md** (release checklist).

## Releases

Maintainers: follow the release checklist in **docs/SHIP_AND_MARKET.md** so tags and the reusable workflow stay aligned.
