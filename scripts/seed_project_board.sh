#!/usr/bin/env bash

set -euo pipefail

if ! command -v gh >/dev/null 2>&1; then
  echo "gh CLI is required (https://cli.github.com/)." >&2
  exit 1
fi

REPO=${REPO:-Balooog/pdfsuite}
MILESTONE=${MILESTONE:-v0.3.0}
LABEL=${LABEL:-$MILESTONE}

label_slug=$(python3 - <<'PY' "$LABEL"
import sys
from urllib.parse import quote
print(quote(sys.argv[1]))
PY
)

if ! gh api "repos/$REPO/labels/$label_slug" >/dev/null 2>&1; then
  echo "Creating label: $LABEL"
  gh label create "$LABEL" --repo "$REPO" --color FFD966 --description "Auto-seeded card label"
fi

if ! gh api "repos/$REPO/milestones?state=all&per_page=100" \
  --jq '.[] | select(.title=="'"$MILESTONE"'") | .number' | grep -q .; then
  echo "Creating milestone: $MILESTONE"
  gh api "repos/$REPO/milestones" -X POST -f title="$MILESTONE" -f state=open \
    -f description="${MILESTONE} release work" >/dev/null
fi

declare -a ITEMS=()

case "$MILESTONE" in
  v0.3.0)
    ITEMS=(
      "CLI coverage expansion::project_board_seed/cli_coverage_expansion.md"
      "Windows smoke parity::project_board_seed/windows_smoke_parity.md"
      "Docs lint enforcement::project_board_seed/doc_lint_enforcement.md"
      "Contributor Guide refresh::project_board_seed/contributor_guide_refresh.md"
    )
    ;;
  v0.4.0)
    ITEMS=(
      "GUI shell MVP::project_board_seed/gui_shell_mvp.md"
      "GUI smoke CI + PyInstaller::project_board_seed/gui_smoke_ci.md"
      "Security & privacy gate::project_board_seed/security_privacy_gate.md"
    )
    ;;
  *)
    echo "No seed items defined for milestone $MILESTONE" >&2
    exit 1
    ;;
esac

for item in "${ITEMS[@]}"; do
  title=${item%%::*}
  body_file=${item##*::}
  if [[ ! -f $body_file ]]; then
    echo "Missing body file: $body_file" >&2
    exit 1
  fi

  echo "Creating issue: $title"
  issue_url=$(gh issue create \
    --repo "$REPO" \
    --title "$title" \
    --body-file "$body_file" \
    --milestone "$MILESTONE" \
    --label "$LABEL")

  issue_number=${issue_url##*/}
  echo " • Created $issue_url"
  echo "   → Add issue #${issue_number} to the repo project board Backlog column."
done

echo "Done. Visit https://github.com/${REPO}/projects to manage cards."
