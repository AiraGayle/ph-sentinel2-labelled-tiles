"""
g4_cut_tiles.py - Group 4: cut 64x64 RGB tiles from one Sentinel-2 L2A scene.

Usage (one scene at a time):
    python g4_cut_tiles.py --safe "path/to/S2A_MSIL2A_....SAFE" --region CEB --out tiles_out

What it does
  1. Reads B04, B03, B02 (10 m) and the SCL cloud layer.
  2. Subtracts the L2A reflectance offset (read from the scene metadata, usually -1000
     for baseline 04.00 and later) so values are comparable to EuroSAT.
  3. Applies ONE fixed stretch (--lo/--hi) to 8-bit. Same numbers for every scene.
  4. Cuts non-overlapping 64x64 tiles. Drops tiles with cloud, shadow, cirrus,
     saturated/defective pixels or no-data. Counts every drop reason.
  5. Saves PNG tiles + a metadata CSV (scene, row, col, UTM x/y, lon/lat, date, cloud).

IMPORTANT: --lo/--hi are placeholders (0, 3000, from the starter code). Replace them
with whatever Member 1 finds for EuroSAT's RGB stretch, and use the same numbers
for EuroSAT and for every Philippine scene.
"""
import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import rasterio
from rasterio.windows import Window
from rasterio.enums import Resampling
from rasterio.warp import transform as warp_transform
from PIL import Image

SIZE = 64
# SCL classes treated as unusable: 0 no data, 1 saturated/defective, 3 cloud shadow,
# 8 cloud medium prob, 9 cloud high prob, 10 thin cirrus
BAD_SCL = [0, 1, 3, 8, 9, 10]


def find_band(safe: Path, name: str, res: str) -> Path:
    hits = sorted(safe.glob(f"GRANULE/*/IMG_DATA/{res}/*_{name}_{res[1:]}.jp2"))
    if not hits:
        sys.exit(f"Could not find {name} at {res} inside {safe}")
    return hits[0]


def read_metadata(safe: Path):
    """Return (processing_baseline, boa_offset, sensing_date) from MTD_MSIL2A.xml."""
    xml = (safe / "MTD_MSIL2A.xml").read_text(encoding="utf-8")

    def first(tag):
        m = re.search(rf"<{tag}[^>]*>\s*([^<]+?)\s*</{tag}>", xml, re.I)
        return m.group(1) if m else None

    baseline = first("PROCESSING_BASELINE")
    date = (first("PRODUCT_START_TIME") or "")[:10]
    offset = first("BOA_ADD_OFFSET")
    offset = int(float(offset)) if offset is not None else 0
    return baseline, offset, date


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--safe", required=True, help="path to the .SAFE folder")
    ap.add_argument("--region", required=True, help="region code, e.g. CEB or CLZ")
    ap.add_argument("--out", required=True, help="output folder (tiles/ and CSV go here)")
    ap.add_argument("--max-cloud", type=float, default=0.0,
                    help="max fraction of bad SCL pixels allowed in a tile (default 0 = none)")
    ap.add_argument("--lo", type=float, default=0.0, help="stretch low (DN after offset)")
    ap.add_argument("--hi", type=float, default=3000.0, help="stretch high (DN after offset)")
    ap.add_argument("--offset", type=int, default=None,
                    help="override the reflectance offset (default: read from metadata)")
    args = ap.parse_args()

    safe = Path(args.safe)
    out = Path(args.out)
    (out / "tiles").mkdir(parents=True, exist_ok=True)

    baseline, meta_offset, date = read_metadata(safe)
    offset = meta_offset if args.offset is None else args.offset
    paths = [find_band(safe, b, "R10m") for b in ("B04", "B03", "B02")]
    scl_path = find_band(safe, "SCL", "R20m")

    # The .SAFE folder may have been renamed (e.g. "Cebu.SAFE"), so take the scene
    # name and tile ID from the band file / GRANULE folder instead of the folder name.
    scene_name = paths[0].parents[2].name            # e.g. L2A_T51PWM_A056614_20260425T022451
    tile_id = paths[0].name.split("_")[0].lstrip("T")  # e.g. 51PWM
    print(f"Scene {scene_name}\n  baseline={baseline}  offset={offset}  date={date}  tile={tile_id}")
    if offset == 0:
        print("  WARNING: offset is 0. If baseline >= 04.00 this is probably wrong; check metadata.")

    drops = {"cloud_or_bad_scl": 0, "nodata": 0}
    rows = []

    with rasterio.open(paths[0]) as r_src, rasterio.open(paths[1]) as g_src, \
         rasterio.open(paths[2]) as b_src, rasterio.open(scl_path) as scl_src:
        H, W = r_src.height, r_src.width
        # SCL is 20 m => exactly half the size of the 10 m bands
        assert scl_src.height * 2 == H and scl_src.width * 2 == W, "SCL size is not half of 10 m"
        crs = r_src.crs
        tf = r_src.transform
        n_rows = H // SIZE
        n_cols = W // SIZE

        for ti in range(n_rows):
            r0 = ti * SIZE
            win = Window(0, r0, n_cols * SIZE, SIZE)
            rgb = np.stack([s.read(1, window=win) for s in (r_src, g_src, b_src)],
                           axis=-1).astype("float32")          # (64, W', 3)
            swin = Window(0, r0 // 2, n_cols * SIZE // 2, SIZE // 2)
            scl = scl_src.read(1, window=swin, out_shape=(SIZE, n_cols * SIZE),
                               resampling=Resampling.nearest)  # (64, W')
            nodata_px = (rgb == 0).all(axis=-1)                # before offset
            rgb = np.clip(rgb + offset, 0, None)
            for tj in range(n_cols):
                c0 = tj * SIZE
                sl = slice(c0, c0 + SIZE)
                if nodata_px[:, sl].any():
                    drops["nodata"] += 1
                    continue
                bad_frac = np.isin(scl[:, sl], BAD_SCL).mean()
                if bad_frac > args.max_cloud:
                    drops["cloud_or_bad_scl"] += 1
                    continue
                tile = np.clip((rgb[:, sl] - args.lo) / (args.hi - args.lo), 0, 1)
                tile = (tile * 255).astype("uint8")
                fname = f"{args.region}_{date.replace('-', '')}_{tile_id}_r{r0:05d}_c{c0:05d}.png"
                Image.fromarray(tile).save(out / "tiles" / fname)
                cx, cy = tf * (c0 + SIZE / 2, r0 + SIZE / 2)
                lon, lat = warp_transform(crs, "EPSG:4326", [cx], [cy])
                rows.append(dict(tile_file=fname, region=args.region, scene=scene_name,
                                 tile_id=tile_id, date=date, row=r0, col=c0,
                                 x_utm=cx, y_utm=cy, crs=str(crs),
                                 lon=lon[0], lat=lat[0], bad_scl_frac=round(float(bad_frac), 4),
                                 label="", subtype="", prelabel=""))
            if ti % 20 == 0:
                print(f"  row {ti}/{n_rows}  kept {len(rows)}")

    csv_path = out / f"tiles_{args.region}_{tile_id}.csv"
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    total = n_rows * n_cols
    summary = dict(scene=scene_name, baseline=baseline, offset=offset, date=date,
                   stretch=[args.lo, args.hi], max_cloud=args.max_cloud,
                   total_grid_tiles=total, kept=len(rows), dropped=drops)
    (out / f"summary_{args.region}_{tile_id}.json").write_text(json.dumps(summary, indent=2))
    print(json.dumps(summary, indent=2))
    print(f"CSV: {csv_path}")


if __name__ == "__main__":
    main()
