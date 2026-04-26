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

SUMMARY_JSON="${WORKDIR}/summary.json"
BREAKING_MD="${WORKDIR}/breaking.md"
CHANGELOG_MD="${WORKDIR}/changelog.md"
BODY="${WORKDIR}/body.md"

oasdiff summary "${BASE_FILE}" "${HEAD_FILE}" -f json >"${SUMMARY_JSON}"
oasdiff breaking "${BASE_FILE}" "${HEAD_FILE}" -f markdown --color never >"${BREAKING_MD}" || true
oasdiff changelog "${BASE_FILE}" "${HEAD_FILE}" -f markdown --color never --level INFO >"${CHANGELOG_MD}" || true

export MARKER COMMENT_TITLE MAX_CHANGELOG_CHARS SPEC_PATH BASE_SHA HEAD_SHA BASE_MODE
export SUMMARY_JSON BREAKING_MD CHANGELOG_MD
python3 "${ROOT}/scripts/render_body.py" >"${BODY}"

PR_NUMBER="$(jq -r .pull_request.number "${GITHUB_EVENT_PATH}")"
export PR_NUMBER
export GITHUB_TOKEN
python3 "${ROOT}/scripts/post_pr_comment.py" "${BODY}"

if [[ "${FAIL_ON_BREAKING,,}" == "true" ]]; then
  echo "Checking for breaking changes (--fail-on ERR)..."
  set +e
  oasdiff breaking "${BASE_FILE}" "${HEAD_FILE}" -f text --color never --fail-on ERR >/dev/null
  st=$?
  set -e
  if [[ "${st}" -ne 0 ]]; then
    echo "::error::Breaking OpenAPI changes detected (oasdiff exit ${st})."
    exit "${st}"
  fi
fi

echo "api-drift-ci: done."
