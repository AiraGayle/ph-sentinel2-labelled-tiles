r"""
g4_targeted_sheets.py - labelling sheets built from the WorldCover first guess.

Usage (run from the project folder):
  python g4_targeted_sheets.py --csvs data\tiles_CEB\tiles_CEB_51PWM_pre.csv data\tiles_CLZ\tiles_CLZ_51PTS_pre.csv --out data\labelling --n 60 --seed 1

Makes, in --out:
  A_<group>_NN.png   numbered 6x6 sheets for annotator A, one group at a time
  annotate_A.csv     sheet, cell, tile_file, region, group, prelabel, label  <- A fills 'label'
  blind_NN.png       numbered sheets of a random mixed subset (no hints) for annotator B
  annotate_B_blind.csv  sheet, cell, tile_file, label                       <- B fills 'label'
Extra batch for short classes:
  python g4_targeted_sheets.py --csvs ... --out data\\labelling2 --groups IndustrialCand NarrowWater --n 60 --exclude data\\labelling\\annotate_A.csv --no-blind
Groups: Forest, AnnualCrop, GrassScrub (HerbaceousVegetation candidates), OpenWater (SeaLake candidates), BuiltUp (Residential/Industrial
candidates), NarrowWater (River candidates). The map cannot tell those pairs apart: you do.
Valid labels: Forest, Residential, Industrial, River, SeaLake, AnnualCrop, HerbaceousVegetation, unsure
"""
import argparse
from pathlib import Path
import pandas as pd
from PIL import Image, ImageDraw

COLS, ROWS, CELL = 6, 6, 160
PER = COLS * ROWS
RULES = {
    "Forest": lambda d: d.wc_Forest >= 0.7,
    "AnnualCrop": lambda d: d.wc_AnnualCrop >= 0.5,
    "OpenWater": lambda d: d.wc_Water >= 0.9,
    "BuiltUp": lambda d: d.wc_BuiltUp >= 0.5,
    "NarrowWater": lambda d: (d.wc_Water >= 0.1) & (d.wc_Water <= 0.5),
    "GrassScrub": lambda d: (d.wc_Grass + d.wc_Shrub) >= 0.5,
}
SIZE_MULT = {"BuiltUp": 1.5, "NarrowWater": 1.5}
HINT = {"IndustrialCand": "Industrial? (bright big roofs)", "Forest": "Forest", "AnnualCrop": "AnnualCrop", "OpenWater": "SeaLake",
        "BuiltUp": "Residential or Industrial?", "NarrowWater": "River?",
        "GrassScrub": "HerbaceousVegetation?"}


def sheet_png(rows, dirs, path):
    img = Image.new("RGB", (COLS * CELL, ROWS * CELL), "white")
    d = ImageDraw.Draw(img)
    for k, r in enumerate(rows):
        im = Image.open(dirs[r["region"]] / r["tile_file"]).convert("RGB")
        im = im.resize((CELL - 4, CELL - 4), Image.BICUBIC)
        x, y = (k % COLS) * CELL, (k // COLS) * CELL
        img.paste(im, (x + 2, y + 2))
        d.rectangle([x + 2, y + 2, x + 30, y + 16], fill="black")
        d.text((x + 5, y + 4), str(k + 1), fill="white")
    img.save(path)


def bright_frac(path):
    """share of pixels that are bright (white or light roofs): a rough 'big roofs' cue."""
    import numpy as np
    a = np.asarray(Image.open(path).convert("RGB"))
    return float((a.max(axis=2) > 200).mean())


def pick(df, n, seed):
    """n tiles, half per region where possible, topped up from the other region."""
    parts = [g for _, g in df.groupby("region")]
    take = []
    for g in parts:
        take.append(g.sample(n=min(len(g), n // max(len(parts), 1)), random_state=seed))
    got = pd.concat(take)
    if len(got) < n:
        rest = df.drop(got.index)
        got = pd.concat([got, rest.sample(n=min(len(rest), n - len(got)), random_state=seed)])
    return got


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csvs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--n", type=int, default=60, help="tiles per group (BuiltUp, NarrowWater x1.5)")
    ap.add_argument("--blind", type=int, default=120, help="size of the blind subset for annotator B")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--groups", nargs="+", default=None,
                    help="only these groups (default: all but IndustrialCand). Add IndustrialCand for factory candidates")
    ap.add_argument("--exclude", nargs="+", default=[], help="CSV(s) of tiles already used (e.g. data\\labelling\\annotate_A.csv)")
    ap.add_argument("--no-blind", action="store_true", help="do not make a blind set (for extra batches)")
    a = ap.parse_args()

    dirs, frames = {}, []
    for c in a.csvs:
        d = pd.read_csv(c)
        for reg in d.region.unique():
            dirs[reg] = Path(c).parent / "tiles"
        frames.append(d)
    df = pd.concat(frames, ignore_index=True)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    if a.exclude:
        seen = set()
        for x in a.exclude:
            seen |= set(pd.read_csv(x).tile_file)
        df = df[~df.tile_file.isin(seen)].reset_index(drop=True)
        print(f"excluded {len(seen)} tiles already used")
    groups = a.groups or list(RULES)

    rows, picked = [], []
    for g in groups:
        if g == "IndustrialCand":
            cand = df[df.wc_BuiltUp >= 0.3].copy()
            cand["bright"] = [bright_frac(dirs[r.region] / r.tile_file) for r in cand.itertuples()]
            sel = cand.sort_values("bright", ascending=False).head(int(a.n * 1.5))
        else:
            sel = pick(df[RULES[g](df)], int(a.n * SIZE_MULT.get(g, 1)), a.seed)
        sel = sel.sample(frac=1, random_state=a.seed)
        picked.append(sel)
        for s in range(0, len(sel), PER):
            chunk = sel.iloc[s:s + PER]
            name = f"A_{g}_{s // PER + 1:02d}"
            sheet_png([r for _, r in chunk.iterrows()], dirs, out / f"{name}.png")
            for k, (_, r) in enumerate(chunk.iterrows()):
                rows.append(dict(sheet=name, cell=k + 1, tile_file=r.tile_file, region=r.region,
                                 group=g, prelabel=HINT[g], label=""))
    A = pd.DataFrame(rows)
    A.to_csv(out / "annotate_A.csv", index=False)
    if a.no_blind:
        print(A.groupby(["group", "region"]).size())
        print(f"A: {len(A)} rows -> {out}")
        return

    pool = A.drop_duplicates("tile_file")
    blind = pool.sample(n=min(a.blind, len(pool)), random_state=a.seed + 100)
    brow = []
    for s in range(0, len(blind), PER):
        chunk = blind.iloc[s:s + PER]
        name = f"blind_{s // PER + 1:02d}"
        sheet_png([dict(tile_file=r.tile_file, region=r.region) for _, r in chunk.iterrows()], dirs, out / f"{name}.png")
        for k, (_, r) in enumerate(chunk.iterrows()):
            brow.append(dict(sheet=name, cell=k + 1, tile_file=r.tile_file, label=""))
    pd.DataFrame(brow).to_csv(out / "annotate_B_blind.csv", index=False)
    print(A.groupby(["group", "region"]).size())
    print(f"A: {len(A)} rows; blind subset for B: {len(brow)} tiles -> {out}")


if __name__ == "__main__":
    main()
