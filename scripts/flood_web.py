"""Display copies of the flood sheets, small enough to put on a map at once.

viz/index.html loads all seven sheets as image sources. At their published size that
is **193 MB of decoded texture**, which is what makes the viewer crawl on an ordinary
laptop - and it buys nothing, because the sheets are a 1.3 m/px *render* of a model
computed on a **10 m grid**. Every pixel below 10 m is drawing, not data.

So this writes a display copy at a quarter of the linear size - about 5 m/px, still
finer than the model - and leaves the full-resolution sheets untouched for QGIS and
for the georeferencing tool, where detail is the point.

The resampling is **max-pooling over the depth class**, not averaging. Averaging RGBA
would invent colours that are not in the legend and would fade thin channels of water
out of existence; taking the deepest class present in each block keeps every wet
pixel wet and keeps the palette exact.

Writes data/derived/viewer/<sheet>.depth.web.png.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from common import DERIVED, log

FACTOR = 4


def main():
    import numpy as np
    from PIL import Image
    viewer = os.path.join(DERIVED, "viewer")
    sheets = sorted(f for f in os.listdir(viewer)
                    if f.endswith(".depth.png") and ".web." not in f)
    if not sheets:
        log("  no depth sheets - run floodmaps.py first")
        return
    before = after = 0
    for fn in sheets:
        src = os.path.join(viewer, fn)
        im = Image.open(src).convert("RGBA")
        a = np.array(im)
        H, W = a.shape[:2]
        before += H * W * 4
        # palette -> class index, ordered by how dark the blue is: deeper water is
        # painted darker, so a lower sum of channels is a deeper class
        flat = a.reshape(-1, 4)
        opaque = flat[flat[:, 3] > 0]
        cols = np.unique(opaque, axis=0)
        order = np.argsort(cols[:, :3].sum(axis=1))[::-1]      # light -> dark
        cols = cols[order]
        idx = np.zeros((H, W), dtype="uint8")
        for i, c in enumerate(cols, start=1):
            idx[np.all(a == c, axis=2)] = i
        h2, w2 = H // FACTOR, W // FACTOR
        pooled = idx[:h2 * FACTOR, :w2 * FACTOR].reshape(
            h2, FACTOR, w2, FACTOR).max(axis=(1, 3))
        out = np.zeros((h2, w2, 4), dtype="uint8")
        for i, c in enumerate(cols, start=1):
            out[pooled == i] = c
        after += h2 * w2 * 4
        dst = src.replace(".depth.png", ".depth.web.png")
        Image.fromarray(out, "RGBA").save(dst, optimize=True)
        log(f"  {fn:26} {W}x{H} -> {w2}x{h2}  "
            f"({os.path.getsize(dst)/1024:.0f} kB, {len(cols)} classes kept)")
    log(f"  decoded texture {before/1e6:.0f} MB -> {after/1e6:.0f} MB "
        f"({before/max(1,after):.0f}x less)")


if __name__ == "__main__":
    main()
