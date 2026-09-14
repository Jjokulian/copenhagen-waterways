"""The nitrogen-pathway register's two counts - how many pathways it lists, and how many
carry no lower bound - counted once, here, for every page that prints them (NITROGEN,
LANDBRUG, LANDING, CAUSATION, OPEN_PROBLEMS), so each is one number with one menu.
"""
import os

import live
from common import MANUAL

REGISTER = os.path.join(MANUAL, "nitrogen_pathways.json")


def counts(P=None):
    """(pathways listed, pathways with no lower bound), live, as fields of the register."""
    P = P if P is not None else live.live_json(REGISTER)
    paths = list(P["pathways"])
    n_unq = sum(1 for p in paths if p["lo"] is None)
    return (live.live(len(paths), P._f, "pathways.n"),
            live.live(n_unq, P._f, "pathways.n_unquantified"))
