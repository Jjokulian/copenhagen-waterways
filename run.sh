#!/usr/bin/env bash
# Full pipeline, start to finish. Safe to re-run: every step caches.
set -euo pipefail
cd "$(dirname "$0")"

python3 scripts/fetch_wfs.py
python3 scripts/fetch_plan_projects.py
python3 scripts/build_registry.py
python3 scripts/report.py
python3 scripts/nitrogen.py
python3 scripts/waves.py || true
python3 scripts/seabed.py || true

# The 2012 flood model, recovered from the PDFs it was published in.
python3 scripts/floodmaps.py fetch
python3 scripts/floodmaps.py render
python3 scripts/floodmaps.py extract
python3 scripts/floodmaps.py autoref     # locates sheets by matching water
python3 scripts/floodmaps.py check       # overlays to confirm by eye
python3 scripts/floodmaps.py georef || true   # hand-placed points, if any

# Does the cloudburst plan go where the water goes?
python3 scripts/floodgap.py || true

python3 scripts/observations.py import || true # no-op until a walk has been logged
python3 scripts/build_viewer_data.py

echo
python3 scripts/floodmaps.py status
echo
echo "Reports:  docs/REGISTER.md   docs/FLOOD_GAP.md   docs/NITROGEN.md"
echo "Serve it: python3 -m http.server 8000"
echo "  map          http://localhost:8000/viz/"
echo "  georeference http://localhost:8000/viz/georef.html   (for the 3 unresolved sheets)"
echo "  field log    http://localhost:8000/viz/log.html      (open on your phone)"
