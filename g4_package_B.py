r"""
g4_package_B.py - make a small zip for the second annotator.

Run from the project folder:
  python g4_package_B.py --csv data\labelling\annotate_B_blind.csv --name label_B_package
  python g4_package_B.py --csv data\labelling2\annotate_B_blind.csv --name label_B2_package

Creates <name>.zip containing label_B.html, annotate_B_blind.csv and only the tile images
that page needs (each tile plus its existing neighbours for the Context panel).
It does NOT include your labels, the map hints or the _pre.csv files, so B stays blind.
B unzips it, double-clicks label_B.html, labels, clicks Export CSV and sends back the CSV.
"""
import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

import pandas as pd


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", required=True)
    ap.add_argument("--name", default="label_B_package")
    ap.add_argument("--data", default="data")
    a = ap.parse_args()

    here = Path(__file__).resolve().parent
    pkg = Path(a.name)
    if pkg.exists():
        shutil.rmtree(pkg)
    pkg.mkdir(parents=True)

    df = pd.read_csv(a.csv)
    keep_cols = [c for c in ("sheet", "cell", "tile_file", "label") if c in df]
    df = df[keep_cols].copy()
    df["label"] = ""                       # B starts from a clean sheet
    csv_out = pkg / "annotate_B_blind.csv"
    df.to_csv(csv_out, index=False)

    n = 0
    for f in df.tile_file:
        m = re.match(r"^(.*)_r(\d{5})_c(\d{5})\.png$", f)
        reg = f.split("_")[0]
        src_dir = Path(a.data) / f"tiles_{reg}" / "tiles"
        dst_dir = pkg / "data" / f"tiles_{reg}" / "tiles"
        dst_dir.mkdir(parents=True, exist_ok=True)
        names = {f}
        if m:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    r, c = int(m[2]) + 64 * dr, int(m[3]) + 64 * dc
                    if r >= 0 and c >= 0:
                        names.add(f"{m[1]}_r{r:05d}_c{c:05d}.png")
        for nm in names:
            s = src_dir / nm
            if s.exists() and not (dst_dir / nm).exists():
                shutil.copy2(s, dst_dir / nm)
                n += 1

    page = here / "g4_label_page.py"
    subprocess.run([sys.executable, str(page), "--csv", str(csv_out), "--mode", "B",
                    "--out", str(pkg / "label_B.html")], check=True)
    (pkg / "README.txt").write_text(
        "1. Unzip this folder.\n2. Double-click label_B.html (opens in your browser).\n"
        "3. For each tile press a key: 1 Forest, 2 Residential, 3 Industrial, 4 River, 5 SeaLake,\n"
        "   6 AnnualCrop, 7 HerbaceousVegetation, 8 unsure. Label on your own, no guessing from others.\n"
        "4. When done, click Export CSV and send back the file annotate_B_labelled.csv.\n", encoding="utf-8")
    z = shutil.make_archive(a.name, "zip", pkg)
    print(f"{n} tile images packed -> {z}")


if __name__ == "__main__":
    main()
