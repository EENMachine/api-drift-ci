#!/usr/bin/env bash
set -euo pipefail

ROOT="${GITHUB_ACTION_PATH:?GITHUB_ACTION_PATH missing}"
MARKER='<!-- api-drift-ci -->'

if [[ "${GITHUB_EVENT_NAME:-}" != "pull_request" ]]; then
  echo "api-drift-ci: skipping (event is ${GITHUB_EVENT_NAME:-unset}, only pull_request is supported)"
  exit 0
fi

BASE_SHA="${GITHUB_EVENT_PULL_REQUEST_BASE_SHA:?}"
HEAD_SHA="${GITHUB_EVENT_PULL_REQUEST_HEAD_SHA:?}"
SPEC="${SPEC_PATH:?}"

WORKDIR="${RUNNER_TEMP}/api-drift-ci"
mkdir -p "${WORKDIR}"
BASE_FILE="${WORKDIR}/base-spec"
HEAD_FILE="${WORKDIR}/head-spec"
EMPTY_SPEC="${WORKDIR}/empty-openapi.yaml"

cat >"${EMPTY_SPEC}" <<'EOF'
openapi: 3.0.0
info:
  title: __api_drift_ci_empty_base__
  version: "0"
paths: {}
EOF

have_object() {
  local sha path
  sha="$1"
  path="$2"
  git cat-file -e "${sha}:${path}" 2>/dev/null
}

if ! have_object "${HEAD_SHA}" "${SPEC}"; then
  echo "::error::Head revision does not contain ${SPEC} (commit ${HEAD_SHA})."
  exit 1
fi

git show "${HEAD_SHA}:${SPEC}" >"${HEAD_FILE}"

if have_object "${BASE_SHA}" "${SPEC}"; then
  git show "${BASE_SHA}:${SPEC}" >"${BASE_FILE}"
  BASE_MODE="file"
else
  cp "${EMPTY_SPEC}" "${BASE_FILE}"
  BASE_MODE="missing-on-base"
fi

OASDIFF_VER="${OASDIFF_VERSION}"
OASDIFF_TGZ="https://github.com/oasdiff/oasdiff/releases/download/v${OASDIFF_VER}/oasdiff_${OASDIFF_VER}_linux_amd64.tar.gz"
echo "Installing oasdiff ${OASDIFF_VER} from ${OASDIFF_TGZ}"
curl -fsSL "${OASDIFF_TGZ}" | tar xz -C "${WORKDIR}"
export PATH="${WORKDIR}:${PATH}"
oasdiff version

OASDIFF_REF_FLAGS=()
if [[ "${ALLOW_EXTERNAL_REFS,,}" == "false" ]]; then
  OASDIFF_REF_FLAGS+=(--allow-external-refs=false)
  echo "oasdiff: external refs disabled (--allow-external-refs=false)"
else
  OASDIFF_REF_FLAGS+=(--allow-external-refs=true)
fi

OASDIFF_IGNORE_FLAGS=()
POLICY_NOTE=""
POLICY_SRC=""

if [[ -n "${POLICY_FILE:-}" ]]; then
  if have_object "${HEAD_SHA}" "${POLICY_FILE}"; then
    POLICY_SRC="${POLICY_FILE}"
  else
    echo "::warning::policy-file was set (${POLICY_FILE}) but is missing on HEAD; skipping policy."
  fi
else
  for f in ".api-drift-ci.toml" "api-drift-ci.toml"; do
    if have_object "${HEAD_SHA}" "$f"; then
      POLICY_SRC="$f"
      break
    fi
  done
fi

if [[ -n "${POLICY_SRC}" ]]; then
  git show "${HEAD_SHA}:${POLICY_SRC}" >"${WORKDIR}/policy.toml"
  if [[ ! -s "${WORKDIR}/policy.toml" ]]; then
    echo "::warning::Policy file ${POLICY_SRC} is empty; skipping."
    POLICY_SRC=""
  fi
fi

if [[ -n "${POLICY_SRC}" ]]; then
  POLICY_JSON="$(python3 "${ROOT}/scripts/parse_policy_toml.py" "${WORKDIR}/policy.toml")"
  ERR_JSON="$(echo "${POLICY_JSON}" | jq -r '.error // empty')"
  if [[ -n "${ERR_JSON}" ]]; then
    echo "::error::Invalid policy TOML (${POLICY_SRC}): ${ERR_JSON}"
    exit 1
  fi
  ERR_REL="$(echo "${POLICY_JSON}" | jq -r '.err_ignore_file // empty')"
  WARN_REL="$(echo "${POLICY_JSON}" | jq -r '.warn_ignore_file // empty')"
  if [[ -n "${ERR_REL}" ]]; then
    if have_object "${HEAD_SHA}" "${ERR_REL}"; then
      git show "${HEAD_SHA}:${ERR_REL}" >"${WORKDIR}/err-ignore.txt"
      if [[ -s "${WORKDIR}/err-ignore.txt" ]]; then
        OASDIFF_IGNORE_FLAGS+=(--err-ignore="${WORKDIR}/err-ignore.txt")
      else
        echo "::warning::err_ignore_file ${ERR_REL} is empty; omitting --err-ignore."
      fi
    else
      echo "::warning::Policy err_ignore_file not found on HEAD: ${ERR_REL}"
    fi
  fi
  if [[ -n "${WARN_REL}" ]]; then
    if have_object "${HEAD_SHA}" "${WARN_REL}"; then
      git show "${HEAD_SHA}:${WARN_REL}" >"${WORKDIR}/warn-ignore.txt"
      if [[ -s "${WORKDIR}/warn-ignore.txt" ]]; then
        OASDIFF_IGNORE_FLAGS+=(--warn-ignore="${WORKDIR}/warn-ignore.txt")
      else
        echo "::warning::warn_ignore_file ${WARN_REL} is empty; omitting --warn-ignore."
      fi
    else
      echo "::warning::Policy warn_ignore_file not found on HEAD: ${WARN_REL}"
    fi
  fi
  if [[ ${#OASDIFF_IGNORE_FLAGS[@]} -gt 0 ]]; then
    POLICY_NOTE="Loaded **${POLICY_SRC}** (repo policy). Active oasdiff ignore file(s): ${#OASDIFF_IGNORE_FLAGS[@]}."
  else
    POLICY_NOTE="Loaded **${POLICY_SRC}**; no ignore files applied (paths missing, empty, or unset)."
  fi
fi

SUMMARY_JSON="${WORKDIR}/summary.json"
BREAKING_MD="${WORKDIR}/breaking.md"
CHANGELOG_MD="${WORKDIR}/changelog.md"
BODY="${WORKDIR}/body.md"

oasdiff summary "${BASE_FILE}" "${HEAD_FILE}" -f json "${OASDIFF_REF_FLAGS[@]}" >"${SUMMARY_JSON}"
oasdiff breaking "${BASE_FILE}" "${HEAD_FILE}" -f markdown --color never "${OASDIFF_REF_FLAGS[@]}" "${OASDIFF_IGNORE_FLAGS[@]}" >"${BREAKING_MD}" || true
oasdiff changelog "${BASE_FILE}" "${HEAD_FILE}" -f markdown --color never --level INFO "${OASDIFF_REF_FLAGS[@]}" "${OASDIFF_IGNORE_FLAGS[@]}" >"${CHANGELOG_MD}" || true

set +e
oasdiff breaking "${BASE_FILE}" "${HEAD_FILE}" -f text --color never --fail-on ERR "${OASDIFF_REF_FLAGS[@]}" "${OASDIFF_IGNORE_FLAGS[@]}" >/dev/null
BREAKING_EXIT=$?
set -e

export MARKER COMMENT_TITLE MAX_CHANGELOG_CHARS SPEC_PATH BASE_SHA HEAD_SHA BASE_MODE
export SUMMARY_JSON BREAKING_MD CHANGELOG_MD
export PRODUCT_REPOSITORY="${PRODUCT_REPOSITORY:-}"
python3 "${ROOT}/scripts/render_body.py" >"${BODY}"

PR_NUMBER="$(jq -r .pull_request.number "${GITHUB_EVENT_PATH}")"
export PR_NUMBER
export GITHUB_TOKEN
python3 "${ROOT}/scripts/post_pr_comment.py" "${BODY}"

export SPEC_PATH BASE_SHA HEAD_SHA FAIL_ON_BREAKING
export BREAKING_EXIT_CODE="${BREAKING_EXIT}"
export BREAKING_MD_PATH="${BREAKING_MD}"
export SUMMARY_JSON_PATH="${SUMMARY_JSON}"
export POLICY_NOTE
export PR_HTML_URL="${PR_HTML_URL:-}"
python3 "${ROOT}/scripts/write_step_summary.py"

if [[ "${FAIL_ON_BREAKING,,}" == "true" ]] && [[ "${BREAKING_EXIT}" -ne 0 ]]; then
  echo "::error::Breaking OpenAPI changes detected (oasdiff exit ${BREAKING_EXIT})."
  exit "${BREAKING_EXIT}"
fi

echo "api-drift-ci: done."
