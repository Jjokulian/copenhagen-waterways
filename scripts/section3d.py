"""Parameters for the dimensioned model of the retrofit, docs/section3d.html.

The model is a *drawn arrangement with stated dimensions*, not a design, and the
distinction only holds if every number in it says where it came from. So the
parameters live here rather than in the page: each one carries a value, a unit, and
a kind - MEASURED if this project computed it from data, STATED if it is an ordinary
design convention adopted here so the geometry can exist at all.

Nearly everything is STATED. That is the honest position: nobody has surveyed a
Copenhagen street for this, and a model that quietly used plausible numbers would be
a design without a designer. The page shows the kind beside every value and lets a
reader move any of them.

Writes docs/data/section3d.json.
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, ROOT, log, read_json


def p(key, label, value, unit, kind, note, lo=None, hi=None, step=None):
    return {"key": key, "label": label, "v": value, "unit": unit, "kind": kind,
            "note": note, "lo": lo, "hi": hi, "step": step}


def main():
    streams = read_json(os.path.join(DERIVED, "streams.json"))
    arch = read_json(os.path.join(ROOT, "docs", "data", "architecture.json"))
    street_m = arch["street_m"]["amager"] + arch["street_m"]["mainland"]
    comb_ha = arch["totals"]["combined"]["ha"]

    params = [
        p("spacing", "Shaft spacing (one bore shot)", 80, "m", "STATED",
          "The shot runs shaft to shaft. Danish street manholes sit closer than a "
          "bore's reach, so spacing is set by the shafts that exist, not by the "
          "method.", 40, 120, 5),
        p("cover", "Cover to the crown of the rain line", 0.90, "m", "STATED",
          "Frost and traffic load set the minimum. Below this the line freezes in a "
          "sag; above it, the rain line starts to compete with the sewer for depth.",
          0.5, 1.6, 0.05),
        p("dn_rain", "Rain line, internal diameter", 250, "mm", "STATED",
          "The variable this page exists to argue about. Sized for the frequent "
          "rain, not for the cloudburst - the surface network takes that. The panel "
          "above computes the smallest diameter that both carries the flow and "
          "still scours, so the slider can be checked against it: bigger is not "
          "safer here, it is slower.", 100, 900, 25),
        p("slope_rain", "Rain line gradient", 8.0, "per mille", "STATED",
          "Guided boring can hold a grade; free-steered drilling cannot, which is "
          "what makes this number decide the method. It also decides whether the "
          "line cleans itself: velocity goes with the square root of it. The rule "
          "of thumb for a minimum is 1/D in millimetres - 4 per mille for a DN250 - "
          "and the head of a network usually needs more than that because the flow "
          "there is small. Watch the fall per shot in the model: at 80 m, 8 per "
          "mille costs 640 mm of depth every shot, which is depth the line does "
          "not have to give.", 1.0, 20.0, 0.5),
        p("dn_sewer", "Existing combined sewer, internal diameter", 1000, "mm",
          "STATED",
          "Typical of an inner-city Copenhagen combined sewer. It was sized for "
          "rain, which is why it is too big for sewage once the rain leaves.",
          400, 2000, 50),
        p("invert_sewer", "Existing sewer invert, below street", 3.50, "m", "STATED",
          "Deep enough to take house drains by gravity. The rain line has to fit "
          "above it without touching what else is in the first metre.",
          2.0, 6.0, 0.1),
        p("dn_liner", "Foul bore, if the sewer is lined down", 300, "mm", "STATED",
          "The fourth arrangement: a pipe sized for the stream it carries, pulled "
          "through the pipe that is already there.", 150, 600, 25),
        p("dn_house", "House drain", 150, "mm", "STATED",
          "Unchanged in every arrangement but the swapped one, which is what makes "
          "the swapped one slow.", 100, 250, 10),
        p("shaft_id", "Shaft, internal diameter", 1250, "mm", "STATED",
          "A standard concrete chamber. It has to hold a person, a ladder and now "
          "a pan that lifts.", 1000, 2000, 50),
        p("ha_served", "Impervious area drained to this shot", 0.21, "ha", "MEASURED",
          f"Derived, not assumed: {street_m/1000:,.0f} km of street inside the "
          f"combined catchments drains {comb_ha:,.0f} impervious hectares, so a "
          f"metre of street carries about {comb_ha*1e4/street_m:.1f} m² and a "
          "shot's worth is the default here. A line near the outlet of a catchment "
          "carries many shots' worth, which is what the slider is for.",
          0.05, 12.0, 0.05),
        p("rain_mm_h", "Design rain", streams["amager"]["design_intensity_mm_h_stated"],
          "mm/h", "STATED",
          "Ordinary heavy rain, well under a cloudburst. The reanalysis record "
          "cannot resolve an hour this wet, which is a limit of the instrument "
          "rather than of Copenhagen.", 2, 30, 1),
        p("runoff_c", "Runoff coefficient", streams["amager"]["runoff_coefficient_stated"],
          "-", "STATED", "Paved surface. Roofs are higher, gardens far lower.",
          0.4, 0.95, 0.05),
        p("manning_n", "Manning roughness of the new line", 0.011, "s/m^(1/3)",
          "STATED",
          "Smooth-bore plastic, fused joints. A concrete sewer is nearer 0.013 and "
          "an old brick one worse than that.", 0.009, 0.016, 0.001),
        p("v_clean", "Self-cleansing velocity", 0.70, "m/s", "STATED",
          "The velocity at which a gravity line carries its own grit rather than "
          "laying it down. The design condition is that it is reached at a stated "
          "frequency, not that it is reached always.", 0.4, 1.2, 0.05),
    ]

    out = {
        "_what": "Dimensions for the retrofit model. Almost all STATED: this is a "
                 "drawn arrangement, not a design, and the kinds say which is which.",
        "_measured_context": {
            "street_km_in_combined_catchments": round(street_m / 1000),
            "combined_impervious_ha": round(comb_ha),
            "m2_impervious_per_m_street": round(comb_ha * 1e4 / street_m, 1),
            "source": "scripts/architecture.py, from the municipal sewer-catchment "
                      "layer and the OSM road extract",
        },
        "params": params,
    }
    path = os.path.join(ROOT, "docs", "data", "section3d.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    log(f"  {len(params)} parameters, "
        f"{sum(1 for x in params if x['kind']=='STATED')} of them stated")
    log(f"  wrote {path}")


if __name__ == "__main__":
    main()
