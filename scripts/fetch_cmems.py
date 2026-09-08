"""Pull Copernicus Marine indicators and gridded ocean colour for Danish waters.

Two jobs, because the catalogue holds two very different kinds of thing.

**Indicators** (the OMI family; the Marine portal groups several of these under
"Ocean Health"). These are already-computed regional series - kilobytes - and
each one is a measured quantity, listed here for what it measures. None of them
is fetched as evidence for or against any hypothesis in the register; they are
fetched because they are variables the register's hypotheses refer to and which
Denmark's own programme does not produce.

  mbi_bottom_salinity      Bottom salinity in the Arkona and Bornholm basins,
                           daily since 1993. Dense saltwater arrives in the
                           Baltic deep basins in episodic pulses through the
                           Danish straits; this index tracks them. A physical
                           driver of deep-water renewal, measured independently
                           of anything on land.
  mbi_sto2tz_gotland       Salinity, temperature and oxygen against depth and
                           time at Gotland Deep - a 240-level, 32-year section.
  cod_volume               The volume of Baltic water where salinity AND oxygen
                           are simultaneously inside cod's tolerance range. A
                           tolerance window computed as a time series by someone
                           else, for a named organism.
  bloom coverage           Summer cyanobacteria bloom extent from space, split
                           into surface, subsurface and concurrent.
  chl area mean / trend    Basin chlorophyll, satellite, 1997-2024, with a
                           failure mode unrelated to Denmark's ship casts.

**Gridded ocean colour**, subset to Danish boxes. Two quantities the national
programme does not produce:

  KD490                    Attenuation, per pixel, daily, since 1997. LIGHT.md's
                           Kd comes from ship casts at stations; this is the same
                           quantity measured by an instrument with a completely
                           different failure mode. Where they disagree, at least
                           one is wrong, and we can say which pixels and when.
  CHL + DIATO/DINO/        Chlorophyll split by what is growing. A single
  CYANOBLOOM/PICO/...      broadband attenuation number does not say what is
                           attenuating; this separates the pigment classes. The
                           split is itself a model applied to reflectance, not a
                           count of cells - it inherits assumptions, and is used
                           here as a second opinion, never as truth.

And the reason to go per-pixel rather than per-area-mean: the standard deviation
INSIDE one polygon on one day is the spatial heterogeneity of that water body.
That is the quantity the one-station-per-water-body assumption needs to be small,
and X14 proposed buying forty sensors to measure it. For optical variables the
archive answers it retrospectively, for the decade already gone, for nothing.

Honest limits, which bound everything downstream:
  * A satellite sees roughly the top optical depth. Bottom water is invisible.
  * Clouds. Denmark loses most days; the daily L3 is mostly gaps in winter.
  * Coastal water is optically complex, and these algorithms are regionally
    tuned but still struggle near shore - exactly where Denmark's fjords are.
    Treat the fjord pixels as weaker than the open-water ones.
  * The 300 m OLCI record starts 2016; only the 1 km multi-sensor record reaches
    back to 1997. Resolution and length trade against each other.
  * These are Baltic-tuned products. West of 9.25E they stop, and the North Sea
    side needs a different product that is not fetched here yet.

Reads   data/derived/areas.json, ~/.copernicusmarine credentials
Writes  data/raw/cmems/indicators/*.nc, data/raw/cmems/grid/*.nc

Usage:  python3 scripts/fetch_cmems.py indicators
        python3 scripts/fetch_cmems.py grid --var KD490 --from 1997-09-04
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import RAW, log, write_json

DEST = os.path.join(RAW, "cmems")

# Danish waters, generously boxed. The Baltic product's western edge is 9.25E,
# so anything west of that (the North Sea proper, the Wadden Sea) needs the NWS
# product instead and is handled as a separate box.
BOXES = {
    "inner": (9.25, 54.4, 13.2, 58.0),   # Kattegat, Belts, Sound, W Baltic
    "arkona": (13.2, 54.4, 15.6, 55.6),  # Bornholm approaches
}

INDICATORS = [
    ("OMI_HEALTH_TEMPSALOXY_BALTIC_mbi_bottom_salinity_arkona_bornholm",
     "Major Baltic Inflow: bottom salinity, Arkona and Bornholm basins"),
    ("OMI_HEALTH_TEMPSALOXY_BALTIC_mbi_sto2tz_gotland",
     "Major Baltic Inflow: depth/time evolution of salinity, temperature, oxygen"),
    ("OMI_HEALTH_TEMPSALOXY_BALTIC_cod_volume",
     "Baltic cod reproductive volume - salinity and oxygen tolerance window"),
    ("OMI_HEALTH_BLOOM_BALTIC_spatiotemporal_coverage",
     "Baltic summer bloom spatiotemporal coverage"),
    ("OMI_HEALTH_CHL_BALTIC_OCEANCOLOUR_area_averaged_mean",
     "Baltic chlorophyll-a basin mean, satellite"),
    ("OMI_HEALTH_CHL_BALTIC_OCEANCOLOUR_trend",
     "Baltic chlorophyll-a trend map, satellite"),
]

GRIDS = {
    # id                                        vars
    "cmems_obs-oc_bal_bgc-transp_my_l3-multi-1km_P1D": ["KD490"],
    "cmems_obs-oc_bal_bgc-plankton_my_l3-multi-1km_P1D":
        ["CHL", "DIATO", "DINO", "CYANOBLOOM", "PICO", "NANO", "MICRO"],
}


def cm():
    import logging
    import warnings
    logging.disable(logging.WARNING)
    warnings.filterwarnings("ignore")
    import copernicusmarine
    return copernicusmarine


def datasets_of(c, product_id):
    p = c.describe(product_id=product_id).products[0]
    return [d.dataset_id for d in (p.datasets or [])]


def do_indicators(a):
    c = cm()
    out = os.path.join(DEST, "indicators")
    os.makedirs(out, exist_ok=True)
    got, failed = [], []
    for pid, why in INDICATORS:
        try:
            dids = datasets_of(c, pid)
        except Exception as e:
            failed.append((pid, f"describe: {type(e).__name__}"))
            log(f"  {pid[:60]:60} describe failed")
            continue
        for did in dids:
            target = os.path.join(out, did + ".nc")
            if os.path.exists(target) and not a.force:
                log(f"  {did[:66]:66} have")
                got.append(did)
                continue
            try:
                r = c.get(dataset_id=did, output_directory=out,
                          no_directories=True, overwrite=True,
                          disable_progress_bar=True)
                # Some OMI datasets publish no original files at all: get()
                # returns success having written nothing. The omi-arco service
                # still has the data, so fall through to it rather than
                # recording a silent zero-byte success.
                if os.path.exists(target) or (getattr(r, "files", None) or []):
                    got.append(did)
                    log(f"  {did[:66]:66} ok")
                    continue
                log(f"  {did[:66]:66} no files; trying arco")
                ds = c.open_dataset(dataset_id=did, service="omi-arco")
                ds.to_netcdf(target)
                ds.close()
                got.append(did)
                log(f"  {did[:66]:66} ok (arco)")
            except Exception as e:
                failed.append((did, f"{type(e).__name__}: {str(e)[:90]}"))
                log(f"  {did[:66]:66} {type(e).__name__}")
    write_json(os.path.join(out, "_manifest.json"),
               {"_what": "Copernicus Marine Ocean Monitoring Indicators for the "
                         "Baltic. Regional indicator series, not gridded fields.",
                "_why": {pid: why for pid, why in INDICATORS},
                "fetched": sorted(got), "failed": failed})
    log(f"\n{len(got)} datasets, {len(failed)} failed -> {out}")
    return 0


def do_grid(a):
    """One file per dataset, per box, per calendar year.

    Chunked by year for three reasons: a refused or interrupted request costs one
    year rather than twenty-eight; peak memory stays at one year of one box
    (~150 MB) instead of the whole cube; and a partial archive is still usable,
    because every year that landed is a complete year.
    """
    c = cm()
    out = os.path.join(DEST, "grid")
    os.makedirs(out, exist_ok=True)
    y0, y1 = int(a.frm[:4]), int(a.to[:4])
    for did, allvars in GRIDS.items():
        vs = [v for v in allvars if not a.var or v in a.var.split(",")]
        if not vs:
            continue
        short = did.split("bgc-")[-1].split("_my_")[0]
        for box, (w, s_, e, n) in BOXES.items():
            if a.box and box != a.box:
                continue
            for y in range(y0, y1 + 1):
                frm = max(f"{y}-01-01", a.frm)
                to = min(f"{y}-12-31", a.to)
                tag = f"{short}__{box}__{y}"
                target = os.path.join(out, tag + ".nc")
                if os.path.exists(target) and not a.force:
                    log(f"  {tag:34} have  {os.path.getsize(target)/1e6:7.1f} MB")
                    continue
                try:
                    c.subset(dataset_id=did, variables=vs,
                             minimum_longitude=w, maximum_longitude=e,
                             minimum_latitude=s_, maximum_latitude=n,
                             start_datetime=frm + "T00:00:00",
                             end_datetime=to + "T23:59:59",
                             output_directory=out, output_filename=tag + ".nc",
                             overwrite=True, disable_progress_bar=True)
                    sz = os.path.getsize(target) / 1e6 if os.path.exists(target) else 0
                    log(f"  {tag:34} ok    {sz:7.1f} MB")
                except Exception as ex:
                    log(f"  {tag:34} FAIL  {type(ex).__name__}: {str(ex)[:110]}")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("what", choices=["indicators", "grid"])
    ap.add_argument("--from", dest="frm", default="1997-09-04")
    ap.add_argument("--to", dest="to", default="2025-12-31")
    ap.add_argument("--var", default="")
    ap.add_argument("--box", default="")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args(argv)
    os.makedirs(DEST, exist_ok=True)
    return do_indicators(a) if a.what == "indicators" else do_grid(a)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
