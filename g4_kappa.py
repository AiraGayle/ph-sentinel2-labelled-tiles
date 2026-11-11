r"""
g4_kappa.py - Cohen's kappa between annotator A and annotator B, plus a disagreement list.

Usage:
  python g4_kappa.py --a data\labelling\annotate_A.csv --b data\labelling\annotate_B_blind.csv --out data\labelling

Compares only tiles both people labelled. Writes disagreements.csv with empty columns
'resolved' and 'how_resolved' to fill in after you discuss each tile.
Kappa is reported twice: on tiles where both gave a class (unsure excluded), and with
'unsure' counted as its own label.
"""
import argparse
from pathlib import Path
import pandas as pd


def kappa(x, y):
    n = len(x)
    if n == 0:
        return float("nan")
    po = (x == y).mean()
    px, py = x.value_counts(normalize=True), y.value_counts(normalize=True)
    pe = sum(px.get(k, 0) * py.get(k, 0) for k in set(px.index) | set(py.index))
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--a", required=True)
    ap.add_argument("--b", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    A = pd.read_csv(args.a)[["tile_file", "label"]].rename(columns={"label": "A"})
    B = pd.read_csv(args.b)[["tile_file", "label"]].rename(columns={"label": "B"})
    m = A.merge(B, on="tile_file").dropna()
    m["A"], m["B"] = m.A.str.strip(), m.B.str.strip()
    m = m[(m.A != "") & (m.B != "")]
    cls = m[(m.A != "unsure") & (m.B != "unsure")]
    print(f"Tiles labelled by both: {len(m)}  (both gave a class: {len(cls)})")
    print(f"Raw agreement (classes only): {(cls.A == cls.B).mean():.3f}")
    print(f"Cohen's kappa (classes only): {kappa(cls.A, cls.B):.3f}")
    print(f"Cohen's kappa (unsure as a label): {kappa(m.A, m.B):.3f}   target >= 0.70")
    print("\nConfusion matrix (rows = A, columns = B):")
    print(pd.crosstab(cls.A, cls.B))
    print("\nAgreement per class (share of A's tiles where B agreed):")
    print(cls.assign(ok=cls.A == cls.B).groupby("A").ok.mean().round(3))
    dis = m[m.A != m.B].copy()
    dis["resolved"] = ""
    dis["how_resolved"] = ""
    path = Path(args.out) / "disagreements.csv"
    dis.to_csv(path, index=False)
    print(f"\n{len(dis)} disagreements written to {path}")


if __name__ == "__main__":
    main()
