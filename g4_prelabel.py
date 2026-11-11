"""
g4_prelabel.py - add an ESA WorldCover first guess to a tile CSV.

Usage:
  python g4_prelabel.py --csv data/tiles_CEB/tiles_CEB_51PWM.csv --maps "scenes" "scenes/Official Maps" --out data/tiles_CEB/tiles_CEB_51PWM_pre.csv

For every tile, samples an 8x8 grid of points inside its 64x64 footprint, looks up the
WorldCover class at each point, and records the share of each class. prelabel is set only
when one group covers >= 70% of the tile. WorldCover has no Industrial or River class,
so built-up and water stay as groups; split them by eye.
"""
import argparse, glob, os
import numpy as np, pandas as pd, rasterio
from rasterio.warp import transform as warp_transform

GROUP = {10: "Forest", 95: "Forest", 40: "AnnualCrop", 50: "BuiltUp", 80: "Water",
         20: "Shrub", 30: "Grass", 60: "Bare", 90: "Wetland", 70: "Other", 100: "Other"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--maps", nargs="+", required=True, help="folders holding WorldCover tifs")
    ap.add_argument("--out", required=True)
    ap.add_argument("--purity", type=float, default=0.7)
    a = ap.parse_args()

    df = pd.read_csv(a.csv)
    tifs = [t for d in a.maps for t in glob.glob(os.path.join(d, "ESA_WorldCover_*_Map.tif"))]
    print("maps:", [os.path.basename(t) for t in tifs])
    crs = df.crs.iloc[0]
    g = (np.arange(8) + 0.5) * 8 - 32            # offsets (m) = pixel centres on 10 m grid
    ox, oy = np.meshgrid(g * 10 / 10, g)          # 8 points per axis, spacing 80 m -> use 10 m px: +-32 px
    ox, oy = ox.ravel() * 10, oy.ravel() * 10     # metres
    X = df.x_utm.values[:, None] + ox[None, :]
    Y = df.y_utm.values[:, None] + oy[None, :]
    lo, la = warp_transform(crs, 'EPSG:4326', X.ravel().tolist(), Y.ravel().tolist())
    lon, lat = np.array(lo).reshape(X.shape), np.array(la).reshape(X.shape)
    cls = np.zeros(lon.shape, dtype="uint8")
    for t in tifs:
        with rasterio.open(t) as s:
            b = s.bounds
            m = (lon >= b.left) & (lon < b.right) & (lat >= b.bottom) & (lat < b.top)
            if not m.any(): continue
            r0, c0 = s.index(lon[m].min(), lat[m].max())
            r1, c1 = s.index(lon[m].max(), lat[m].min())
            r0, c0, r1, c1 = max(r0 - 1, 0), max(c0 - 1, 0), r1 + 2, c1 + 2
            from rasterio.windows import Window
            win = Window(c0, r0, c1 - c0, r1 - r0)
            arr = s.read(1, window=win)
            rr, cc = rasterio.transform.rowcol(s.window_transform(win), lon[m], lat[m])
            rr = np.clip(rr, 0, arr.shape[0] - 1); cc = np.clip(cc, 0, arr.shape[1] - 1)
            cls[m] = arr[rr, cc]
            print("read", os.path.basename(t), arr.shape)
    groups = np.vectorize(lambda v: GROUP.get(v, "Other"))(cls)
    names = ["Forest", "AnnualCrop", "BuiltUp", "Water", "Grass", "Shrub", "Bare", "Wetland", "Other"]
    for n in names:
        df["wc_" + n] = (groups == n).mean(axis=1).round(3)
    frac = df[["wc_" + n for n in names]]
    df["wc_dominant"] = frac.idxmax(axis=1).str[3:]
    df["wc_frac"] = frac.max(axis=1)
    df["prelabel"] = np.where(df.wc_frac >= a.purity, df.wc_dominant, "")
    df.to_csv(a.out, index=False)
    print(df.prelabel.replace("", "mixed").value_counts())

if __name__ == "__main__":
    main()
