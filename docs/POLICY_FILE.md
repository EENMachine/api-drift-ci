# Repo policy file (`.api-drift-ci.toml`)

**API Drift CI** can load a small **TOML** file from the **pull request head** commit and pass allowlisted ignore files to [oasdiff](https://github.com/oasdiff/oasdiff) (`--err-ignore` / `--warn-ignore`). That gives you a **versioned, reviewable policy layer** without changing how breaking changes are defined (still oasdiff rules).

## Discovery order

1. If the workflow sets the action input **`policy-file`**, that path is used (must exist on **HEAD**).
2. Otherwise, if **`.api-drift-ci.toml`** exists on HEAD, it is used.
3. Otherwise, if **`api-drift-ci.toml`** exists on HEAD, it is used.
4. If none of the above exist, no policy is applied.

## Format

```toml
# Paths are repo-relative on the PR branch (no ".." segments, not absolute).
err_ignore_file = ".github/oasdiff-err-ignore.txt"
warn_ignore_file = ".github/oasdiff-warn-ignore.txt"
```

Each referenced file must exist on **HEAD**. Empty files are skipped with a warning.

The ignore files use **oasdiff’s native format** (text patterns per [oasdiff breaking change docs](https://github.com/oasdiff/oasdiff/blob/main/docs/BREAKING-CHANGES.md)). This action does not invent a second ignore syntax.

## Security note

Policy and ignore files are taken from the **PR head** branch. For **fork** pull requests, treat them like any other contributor-controlled config: review changes carefully and combine with `allow-external-refs: false` when appropriate ([SECURITY.md](../SECURITY.md)).

## Automation outputs

The composite action also sets **`breaking-exit-code`** (and the reusable workflow forwards it as a job output) so other steps can branch on the same oasdiff verdict. See the [README](../README.md) “Action outputs” section.
