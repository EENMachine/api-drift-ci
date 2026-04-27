# Customer FAQ

## The workflow says “Head revision does not contain …”

The path in `spec-path` must exist on the **PR head** commit. Check spelling, case sensitivity on Linux runners, and that the file is committed on the branch you opened the PR from.

## The comment never appears

1. Confirm `permissions: pull-requests: write` (or equivalent org policy) on the workflow job.
2. Confirm the event is **`pull_request`** (the action skips other events by design).
3. For **fork** pull requests, repository settings may restrict `GITHUB_TOKEN` from writing to the base repo; see [GitHub docs on fork PRs](https://docs.github.com/en/actions/security-guides/security-hardening-for-github-actions).

## I need `git show` to work but checkout is shallow

Use `actions/checkout@v4` with **`fetch-depth: 0`** so both base and head SHAs are available for `git show <sha>:path`.

## Should I use the composite action or the reusable workflow?

- **Composite** (`uses: EENMachine/api-drift-ci@v…`): maximum control in your own workflow YAML.
- **Reusable workflow**: smallest footprint in each service repo; pin the workflow ref you trust.

## Fork PRs and external `$ref` in OpenAPI

If you run workflows on untrusted fork PRs, set **`allow-external-refs`** to **`false`** so oasdiff does not resolve remote references (see [SECURITY.md](../SECURITY.md)). Legitimate specs that rely on external `$ref` may need `true`.

## Does this run on Windows or macOS runners?

Not today: the action downloads the **Linux amd64** oasdiff binary. Use **`runs-on: ubuntu-latest`**.

## Where do breaking rules come from?

From **[oasdiff](https://github.com/oasdiff/oasdiff)**. This action does not redefine “breaking”; it surfaces oasdiff’s report in the PR.

## Where is the result if I do not read PR comments?

Open the workflow run on GitHub → tab **Summary**. This action appends a **job summary** (verdict, oasdiff exit code, excerpt, link to the PR) on every run via `$GITHUB_STEP_SUMMARY`.

## How do I suppress known breaking findings in CI?

Add a repo policy file (see [**POLICY_FILE.md**](POLICY_FILE.md)): **`.api-drift-ci.toml`** on your PR branch can point to oasdiff-native **`err_ignore_file`** / **`warn_ignore_file`** text files. Ignores are applied to **breaking** and **changelog** oasdiff runs (not to the JSON **summary** step).

## Can a later workflow step read the oasdiff exit code?

Yes. The composite action sets the output **`breaking-exit-code`** (and writes **`0`** when the event is skipped because it is not `pull_request`). Give the step an `id` and use `steps.<id>.outputs.breaking-exit-code`. The reusable workflow forwards the same value as **`jobs.<job_id>.outputs.breaking-exit-code`**.
