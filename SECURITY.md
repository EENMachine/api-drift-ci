# Security policy

## Supported versions

We address security issues in the latest minor release on the default branch (`master`) and in the latest published semver tag.

## Reporting a vulnerability

Please open a **private vulnerability report** via GitHub (**Security** tab → **Report a vulnerability**) for this repository, or email the maintainers if that interface is unavailable. Include reproduction steps and impact. We will acknowledge receipt as soon as we can.

## Threat model notes

### OpenAPI external references

Specs can contain `$ref` to external URLs. oasdiff may fetch those by default. For **pull requests from forks** (untrusted contributors), consider setting the action input **`allow-external-refs`** to **`false`** so resolution of remote refs is disabled. This may break specs that legitimately depend on external refs.

### `GITHUB_TOKEN`

The action needs **`pull-requests: write`** to upsert the PR comment. Use the default `github.token` only in workflows you trust; follow GitHub’s guidance for [fork PR workflows](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions).

### Runner and supply chain

The action downloads a pinned **oasdiff** release tarball from GitHub Releases (`oasdiff/oasdiff`). The composite runs on **`ubuntu-latest`**. Review releases before upgrading the default `oasdiff-version` input.

### Policy and ignore files

Optional **`.api-drift-ci.toml`** (or the `policy-file` input) and the referenced ignore files are read from the **pull request head** commit, like your OpenAPI spec. For **fork** PRs, treat policy changes as contributor-controlled configuration and review them like code.

### Operational questions

For checkout depth, fork PRs, and token permissions, see [**docs/FAQ.md**](docs/FAQ.md).
