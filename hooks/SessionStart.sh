#!/usr/bin/env bash
# SessionStart hook for strategic-analyst plugin.
#
# Reads .env.example and .env from the plugin root, lists which API keys are
# present, missing, or empty, and injects a one-line-per-key summary into the
# session context. Never blocks — analysts may legitimately run with a partial
# credential set; the warning is so they know which sources are dark today.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
PLUGIN_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

ENV_FILE="${PLUGIN_ROOT}/.env"
ENV_EXAMPLE="${PLUGIN_ROOT}/.env.example"

# Collect the key names declared in .env.example (lines like FOO_KEY=)
declared_keys=()
if [ -f "${ENV_EXAMPLE}" ]; then
    while IFS= read -r line; do
        # Skip comments and blank lines
        [[ "${line}" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        # Extract the LHS of the first =
        key="${line%%=*}"
        key="${key// }"
        if [[ -n "${key}" && "${key}" =~ ^[A-Z_][A-Z0-9_]*$ ]]; then
            declared_keys+=("${key}")
        fi
    done < "${ENV_EXAMPLE}"
fi

# Load .env values if present
declare -A env_values
if [ -f "${ENV_FILE}" ]; then
    while IFS= read -r line; do
        [[ "${line}" =~ ^[[:space:]]*# ]] && continue
        [[ -z "${line// }" ]] && continue
        key="${line%%=*}"
        val="${line#*=}"
        key="${key// }"
        # Strip surrounding quotes from val
        val="${val%\"}"
        val="${val#\"}"
        env_values["${key}"]="${val}"
    done < "${ENV_FILE}"
fi

# Build a summary list
present=()
missing=()
for key in "${declared_keys[@]}"; do
    val="${env_values[${key}]:-}"
    if [ -n "${val}" ]; then
        present+=("${key}")
    else
        missing+=("${key}")
    fi
done

# Build human-readable summary
summary_lines=("strategic-analyst plugin — credential check")
if [ ! -f "${ENV_FILE}" ]; then
    summary_lines+=("  .env not found at ${ENV_FILE}")
    summary_lines+=("  copy .env.example to .env and fill in keys you have; missing keys are non-fatal")
else
    summary_lines+=("  .env loaded from ${ENV_FILE}")
fi
summary_lines+=("  ${#present[@]} keys set, ${#missing[@]} missing")
if [ "${#missing[@]}" -gt 0 ]; then
    summary_lines+=("  dark sources this session: ${missing[*]}")
fi

# Watchlist check
WATCHLIST="${PLUGIN_ROOT}/config/watchlist.yaml"
WATCHLIST_EXAMPLE="${PLUGIN_ROOT}/config/watchlist.example.yaml"
if [ ! -f "${WATCHLIST}" ]; then
    if [ -f "${WATCHLIST_EXAMPLE}" ]; then
        summary_lines+=("  config/watchlist.yaml not found; daily-sitrep will use config/watchlist.example.yaml as fallback")
    else
        summary_lines+=("  config/watchlist.yaml not found and no example present — daily-sitrep will not function")
    fi
fi

# Build the additionalContext as a single string with literal \n separators
context=""
for line in "${summary_lines[@]}"; do
    context+="${line}\n"
done

# Escape for JSON
escape_for_json() {
    local s="$1"
    s="${s//\\/\\\\}"
    s="${s//\"/\\\"}"
    s="${s//$'\n'/\\n}"
    s="${s//$'\r'/\\r}"
    s="${s//$'\t'/\\t}"
    printf '%s' "$s"
}
context_escaped=$(escape_for_json "${context}")

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": "${context_escaped}"
  }
}
EOF

exit 0
