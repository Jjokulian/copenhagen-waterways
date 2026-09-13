#!/usr/bin/env python3
"""Which of a script's input files a given output field actually rests on, read from the
code (ast). Start at the statement that writes the field's key; follow the names it
uses backwards through the function (assignments, loop targets, calls that fill a
name), into the local helper functions it calls (all their file reads), and out
through parameters to the callers that pass them.

Static and approximate. It cannot follow data that passes through a file whose path
is built at run time - a cache in a temporary folder, say - so a file it does not
reach may still be one the field rests on. flows_store.py therefore uses the answer
to draw the traced files as the chain and to list the others beside it as read by
the script but not traced to the number: nothing is removed on its strength alone.

Results are cached by the script's own content, so an unchanged script is not traced
again when the index is written.
"""
import ast
import glob
import hashlib
import json
import os

from common import ROOT

BASE = {"ROOT": {""}, "DERIVED": {"data/derived"}, "RAW": {"data/raw"}, "MANUAL": {"data/manual"}}
READ = {"read_json", "load", "open", "loadtxt", "fromfile", "read_csv", "live_json", "genfromtxt",
        "memmap", "read_excel", "read_file", "load_json", "GzipFile"}
CACHE = os.path.join(os.environ.get("TMPDIR", "/tmp"), "copenhagen-io-trace.json")
_CONSTS, _MODS = {}, {}


def _res(n, names):
    """The set of paths an expression may stand for (empty: not readable from code)."""
    if isinstance(n, ast.Constant) and isinstance(n.value, str):
        return {n.value}
    if isinstance(n, ast.Name):
        return set(names.get(n.id, set()))
    if isinstance(n, ast.JoinedStr):
        return {"".join(v.value if isinstance(v, ast.Constant) else "*" for v in n.values)}
    if isinstance(n, ast.Call):
        a = getattr(n.func, "attr", None)
        if a in ("abspath", "realpath", "normpath") and n.args:
            return _res(n.args[0], names)
        if a == "dirname" and n.args:
            i = n.args[0]
            if (isinstance(i, ast.Name) and i.id == "__file__") or (
                    isinstance(i, ast.Call) and i.args and isinstance(i.args[0], ast.Name)
                    and i.args[0].id == "__file__"):
                return {"scripts"}
            return {os.path.dirname(p) for p in _res(i, names)}
        if a == "join" and getattr(getattr(n.func, "value", None), "attr", None) == "path":
            combos = [""]
            for x in n.args:
                r = _res(x, names)
                if not r:
                    return set()
                combos = [os.path.join(c, y) if c else y for c in combos for y in r]
            return {os.path.normpath(c) for c in combos}
    if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Add):
        a, b = _res(n.left, names), _res(n.right, names)
        return {x + y for x in a for y in b} if a and b else set()
    return set()


def _pathlike(p):
    return "/" in p or p.endswith((".json", ".csv", ".gz", ".npy", ".bin", ".geojson", ".tif", ".nc"))


def _consts(path):
    """Path constants a script defines or imports from a sibling script."""
    if path in _CONSTS:
        return _CONSTS[path]
    _CONSTS[path] = names = {k: set(v) for k, v in BASE.items()}
    try:
        tree = ast.parse(open(os.path.join(ROOT, path), encoding="utf-8").read())
    except (OSError, SyntaxError):
        return names
    for node in tree.body:
        if isinstance(node, ast.ImportFrom) and node.module and not node.level:
            sib = os.path.join("scripts", node.module + ".py")
            if os.path.exists(os.path.join(ROOT, sib)):
                got = _consts(sib)
                for al in node.names:
                    if al.name in got:
                        names[al.asname or al.name] = set(got[al.name])
    for _ in range(3):
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign) and len(node.targets) == 1 and isinstance(node.targets[0], ast.Name):
                v = {p for p in _res(node.value, names) if _pathlike(p)}
                if v:
                    names.setdefault(node.targets[0].id, set()).update(v)
    return names


class _Mod:
    def __init__(self, path):
        self.tree = ast.parse(open(os.path.join(ROOT, path), encoding="utf-8").read())
        self.names = _consts(path)
        self.funcs = {f.name: f for f in ast.walk(self.tree)
                      if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef))}
        self.parent = {}
        for f in self.funcs.values():
            for n in ast.walk(f):
                self.parent.setdefault(n, f)
        self._local, self._assign = {}, {}

    def names_in(self, f):
        if f is None:
            return self.names
        if id(f) not in self._local:
            names = {k: set(v) for k, v in self.names.items()}
            for n in ast.walk(f):
                if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name):
                    v = {p for p in _res(n.value, names) if "/" in p}
                    if v:
                        names.setdefault(n.targets[0].id, set()).update(v)
            self._local[id(f)] = names
        return self._local[id(f)]

    def reads(self, node, f):
        names, out = self.names_in(f), set()
        for c in ast.walk(node):
            if isinstance(c, ast.Call) and c.args:
                fn = getattr(c.func, "id", None) or getattr(c.func, "attr", None)
                if fn in READ:
                    out |= {p for p in _res(c.args[0], names)
                            if p.startswith(("data/", "docs/data/", "../", "/"))}
        return out

    def calls(self, node):
        return {getattr(c.func, "id", None) for c in ast.walk(node) if isinstance(c, ast.Call)} & set(self.funcs)

    def assigning(self, f, name):
        """Statements in f (or the module) that give `name` a value, indexed once."""
        k = id(f)
        if k not in self._assign:
            idx = {}
            for s in ast.walk(f if f is not None else self.tree):
                tg = []
                if isinstance(s, ast.Assign):
                    tg = s.targets
                elif isinstance(s, (ast.AugAssign, ast.AnnAssign)):
                    tg = [s.target]
                elif isinstance(s, (ast.For, ast.comprehension)):
                    tg = [s.target]
                elif isinstance(s, ast.withitem) and s.optional_vars is not None:
                    tg = [s.optional_vars]
                for t in tg:
                    for x in ast.walk(t):
                        if isinstance(x, ast.Name):
                            idx.setdefault(x.id, []).append(s)
            self._assign[k] = idx
        return self._assign[k].get(name, [])


def _mod(path):
    if path not in _MODS:
        _MODS[path] = _Mod(path)
    return _MODS[path]


def _field_files(path, key):
    m = _mod(path)
    hits = [n for n in ast.walk(m.tree) if isinstance(n, ast.Constant) and n.value == key]
    if not hits:
        return None
    files, done, seen = set(), set(), set()

    def whole(fname, depth=0):
        if fname in done or depth > 6:
            return
        done.add(fname)
        f = m.funcs[fname]
        files.update(m.reads(f, f))
        for g in m.calls(f):
            whole(g, depth + 1)

    def trace(f, names, depth=0):
        todo = list(names)
        while todo:
            nm = todo.pop()
            if (id(f), nm) in seen or depth > 8:
                continue
            seen.add((id(f), nm))
            for s in m.assigning(f, nm):
                src = s.iter if isinstance(s, (ast.For, ast.comprehension)) else (
                    getattr(s, "value", None) or getattr(s, "context_expr", None) or s)
                files.update(m.reads(src, f))
                for g in m.calls(src):
                    whole(g)
                todo += [x.id for x in ast.walk(src) if isinstance(x, ast.Name)]
            if f is not None and nm in [a.arg for a in f.args.args]:
                pos = [a.arg for a in f.args.args].index(nm)
                for c in ast.walk(m.tree):
                    if isinstance(c, ast.Call) and getattr(c.func, "id", None) == f.name and len(c.args) > pos:
                        trace(m.parent.get(c), [x.id for x in ast.walk(c.args[pos]) if isinstance(x, ast.Name)],
                              depth + 1)

    h = hits[0]
    f = m.parent.get(h)
    stmt = h
    for s in ast.walk(f if f is not None else m.tree):
        if isinstance(s, ast.stmt) and not isinstance(s, (ast.FunctionDef, ast.If, ast.For, ast.While, ast.With, ast.Try)) \
                and any(x is h for x in ast.walk(s)):
            stmt = s
    files.update(m.reads(stmt, f))
    for g in m.calls(stmt):
        whole(g)
    trace(f, [x.id for x in ast.walk(stmt) if isinstance(x, ast.Name)])
    out = set()
    for p in files:
        out |= set(os.path.relpath(x, ROOT) for x in glob.glob(os.path.join(ROOT, p))) if "*" in p else {p}
    return sorted(out)


_cache = None


def field_files(path, key):
    """The files the field `key` written by `path` is traced to (None: key not found)."""
    global _cache
    if _cache is None:
        try:
            _cache = json.load(open(CACHE, encoding="utf-8"))
        except (OSError, ValueError):
            _cache = {}
    try:
        sha = hashlib.sha1(open(os.path.join(ROOT, path), "rb").read()).hexdigest()
    except OSError:
        return None
    entry = _cache.get(path)
    if not entry or entry.get("sha") != sha:
        entry = _cache[path] = {"sha": sha, "keys": {}}
    if key not in entry["keys"]:
        try:
            entry["keys"][key] = _field_files(path, key)
        except (SyntaxError, RecursionError, KeyError):
            entry["keys"][key] = None
    return entry["keys"][key]


def save_cache():
    if _cache is not None:
        tmp = CACHE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(_cache, f)
        os.replace(tmp, CACHE)
