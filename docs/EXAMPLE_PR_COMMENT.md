# Example PR comment (illustrative)

What your team sees on a pull request (structure and tone; exact wording comes from [oasdiff](https://github.com/oasdiff/oasdiff) for your spec).

```markdown
<!-- api-drift-ci -->
## OpenAPI drift

**Spec:** `docs/openapi.yaml`  
**Base:** `a1b2c3d` → **Head:** `e4f5g6h`

### Policy

_(Optional; only when `.api-drift-ci.toml` / `policy-file` is used.)_  
Loaded **`.api-drift-ci.toml`**. Active oasdiff ignore file(s): 1.

### Summary

Endpoints: deleted **1**. Paths: deleted **1**.

### Breaking changes

## GET,/pets

### ❌ Breaking

#### API path removed without deprecation

### Full changelog

…(markdown changelog from oasdiff)…

---

_Posted by [**api-drift-ci**](https://github.com/EENMachine/api-drift-ci). Powered by [oasdiff](https://github.com/oasdiff/oasdiff)._
```

The HTML comment at the top is how the action finds and **updates** the same comment when you push new commits to the PR.
