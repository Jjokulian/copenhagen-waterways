#!/usr/bin/env bash
# The NetCDF/satellite stack, which is not in the base image.
#
# Fedora ships ensurepip but not the python3-pip rpm, so `python3 -m pip` fails out
# of the box and it looks like pip is unavailable. It is not - it is bundled in
# ensurepip and a venv brings it up. This has nothing to do with memory or disk.
#
# Everything goes in a venv rather than system python: Fedora's is externally
# managed, and the project should not need root to be reproducible.
#
#   ./scripts/setup_venv.sh && ~/.venvs/marine/bin/python your_script.py
set -euo pipefail
VENV="${1:-$HOME/.venvs/marine}"

python3 -m venv "$VENV"
"$VENV/bin/pip" install --quiet --upgrade pip
"$VENV/bin/pip" install --quiet \
    netCDF4 \
    xarray \
    copernicusmarine

"$VENV/bin/python" - <<'PY'
import netCDF4, xarray, copernicusmarine
print(f"  netCDF4          {netCDF4.__version__}")
print(f"  xarray           {xarray.__version__}")
print(f"  copernicusmarine {copernicusmarine.__version__}")
PY
echo "  venv at $VENV (~212 MB, gitignored)"
