#!/usr/bin/env bash
# Full pipeline, start to finish. Safe to re-run: every step caches.
set -euo pipefail
cd "$(dirname "$0")"
python3 scripts/fetch_wfs.py
python3 scripts/fetch_plan_projects.py
python3 scripts/build_registry.py
python3 scripts/report.py
python3 scripts/build_viewer_data.py
echo
echo "Done. Serve it:  python3 -m http.server 8000   ->  http://localhost:8000/viz/"
