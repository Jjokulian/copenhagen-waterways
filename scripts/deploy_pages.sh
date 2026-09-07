#!/usr/bin/env bash
# Create the GitHub repository, push, and let the Actions workflow turn Pages on.
#
# Needs a GitHub token, because repository creation has no SSH equivalent - an SSH key
# can push to a repo that exists but cannot bring one into being, and cannot enable Pages.
# A classic token needs `repo` and `workflow`; a fine-grained one needs Administration:
# write, Contents: write, Workflows: write, and Pages: write on the target account.
#
#   GH_TOKEN=... ./scripts/deploy_pages.sh [owner] [repo]
#
# The push itself goes over SSH (the key on this machine already authenticates as
# Jjokulian), so the token is used only for the two API calls and never written to
# .git/config or a remote URL.
set -euo pipefail
cd "$(dirname "$0")/.."

OWNER="${1:-Jjokulian}"
REPO="${2:-copenhagen-waterways}"
API="https://api.github.com"

if [ -z "${GH_TOKEN:-}" ]; then
  echo "GH_TOKEN is not set." >&2
  echo "Create one at https://github.com/settings/tokens with 'repo' + 'workflow' scope," >&2
  echo "then re-run:  GH_TOKEN=ghp_... ./scripts/deploy_pages.sh" >&2
  exit 1
fi

api() { curl -sS --fail-with-body -H "Authorization: Bearer $GH_TOKEN" \
        -H "Accept: application/vnd.github+json" \
        -H "X-GitHub-Api-Version: 2022-11-28" "$@"; }

echo "==> checking token"
who=$(api "$API/user" | python3 -c 'import sys,json; print(json.load(sys.stdin)["login"])')
echo "    authenticated as $who"

echo "==> repository $OWNER/$REPO"
if api "$API/repos/$OWNER/$REPO" >/dev/null 2>&1; then
  echo "    already exists, reusing"
else
  # Public on purpose: Pages on a private repository needs a paid plan, and this is
  # an open-data project with nothing to withhold.
  body=$(python3 - "$REPO" <<'PY'
import json,sys
print(json.dumps({
  "name": sys.argv[1],
  "description": "Copenhagen's sewers, cloudburst infrastructure and discharge points, "
                 "from open data - including the 2012 flood model recovered from PDF.",
  "homepage": "",
  "private": False,
  "has_issues": True, "has_wiki": False, "has_projects": False,
  "auto_init": False,
}))
PY
)
  if [ "$who" = "$OWNER" ]; then
    api -X POST "$API/user/repos" -d "$body" >/dev/null
  else
    api -X POST "$API/orgs/$OWNER/repos" -d "$body" >/dev/null
  fi
  echo "    created (public)"
fi

echo "==> pushing over SSH"
git remote get-url origin >/dev/null 2>&1 \
  && git remote set-url origin "git@github.com:$OWNER/$REPO.git" \
  || git remote add origin "git@github.com:$OWNER/$REPO.git"
git push -u origin main

echo "==> waiting for the Pages deployment"
# The workflow calls actions/configure-pages with enablement:true, so Pages switches
# itself on during the first run. That first run also has to upload ~34 MB, so give it
# a few minutes before deciding something is wrong.
url=""
for i in $(seq 1 40); do
  if out=$(api "$API/repos/$OWNER/$REPO/pages" 2>/dev/null); then
    url=$(printf '%s' "$out" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("html_url") or "")')
    status=$(printf '%s' "$out" | python3 -c 'import sys,json; print(json.load(sys.stdin).get("status") or "")')
    [ -n "$url" ] && [ "$status" = "built" ] && break
  fi
  sleep 15
  printf '.'
done
echo

if [ -z "$url" ]; then
  url="https://$(printf '%s' "$OWNER" | tr 'A-Z' 'a-z').github.io/$REPO/"
  echo "Pages has not reported built yet. Watch the run at:"
  echo "  https://github.com/$OWNER/$REPO/actions"
  echo "It should appear at $url"
else
  echo "Live: $url"
fi

command -v xdg-open >/dev/null && xdg-open "$url" >/dev/null 2>&1 &
echo "Repository: https://github.com/$OWNER/$REPO"
