# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) once we reach v1.0.0.

## [Unreleased]

## [0.1.0] - 2026-04-26

### Added

- Composite GitHub Action: diff OpenAPI at PR base vs head, sticky PR comment, optional fail on breaking.
- `allow-external-refs` input (passed through to oasdiff).
- Reusable workflow `.github/workflows/reusable-openapi-drift.yml` for one-line adoption from other repos.
- CI workflow (`bash -n`, Python compile).
- Documentation: shipping/marketing playbook, security notes, contributing.

[Unreleased]: https://github.com/EENMachine/api-drift-ci/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/EENMachine/api-drift-ci/releases/tag/v0.1.0
