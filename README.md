# Philippine Sentinel-2 labelled tiles (Track A: EuroSAT to Philippine Sentinel-2)

A small, documented set of Philippine Sentinel-2 tiles, labelled by two annotators, used to test a model trained on EuroSAT.

- **Tiles:** 64×64 px, 10 m, true colour, from two scenes (CEB: T51PWM, 2026-04-25; CLZ: T51PTS, 2026-10-15).
- **Examined:** 901 tiles. **Labelled:** 717. **Unsure (excluded):** 184.
- **Classes:** Forest, HerbaceousVegetation, AnnualCrop, Residential, Industrial, River, SeaLake.
- **Agreement:** Cohen's kappa 0.853 on real classes only (515 tiles), 0.567 with unsure as a label (901 tiles).

## Where things are
| Path | What it is |
|---|---|
| `data/labels/labels_for_model.csv` | The file to score a model against: `tile_file`, `region`, `label`, `both_agree`. |
| `data/labels/labels_all.csv` | All 901 tiles with both annotators' labels, the final label and how it was resolved. |
| `data/labels/counts_by_class.csv` | Class counts. |
| `data/labels/disagreements.csv` | The tiles the annotators disagreed on, with the resolution. |
| `data/labels/kappa/` | One label file per annotator, for the kappa script. |
| `data/tiles_labelled/` | The 901 tile images (PNG). |
| `docs/` | Labelling protocol, data card, disagreement resolution, AI use, example tiles. |
| `g4_*.py` | Scripts used to cut tiles, build labelling sheets and compute kappa. |

## Scoring a model
Compare the model's prediction for each tile in `labels_for_model.csv` with `label`. Also report accuracy on the tiles where `both_agree` is `yes`, because those labels are the most reliable. River and Herbaceous are the least reliable classes.

## Recomputing kappa
```
python g4_kappa.py --a data/labels/kappa/rater_person1.csv --b data/labels/kappa/rater_claude.csv --out data/labels
```

## Notes
The second annotator was an AI (see `docs/AI_USE.md`). The set is not a random sample of the Philippines. Sentinel-2 data are free and open (Copernicus); ESA WorldCover (used only as a hint) is CC BY 4.0.
