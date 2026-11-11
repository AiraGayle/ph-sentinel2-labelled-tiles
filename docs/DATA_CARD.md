# Data card — Philippine Sentinel-2 labelled tiles (Track A test set)

## Summary
A small labelled set of Philippine Sentinel-2 tiles built to test how well a model trained on EuroSAT carries over to the Philippines. 901 tiles were examined; 717 have a class label and 184 were left unsure and are excluded from scoring.

## Source imagery
| | CEB | CLZ |
|---|---|---|
| Sentinel-2 tile | T51PWM | T51PTS |
| Acquisition date | 2026-04-25 | 2026-10-15 |
| Product | L2A | L2A |
| Candidate 64×64 tiles cut | 20,942 | 22,607 |
| Tiles labelled | 443 | 458 |

Bands: B04, B03, B02 (true colour), 10 m, fixed stretch 0–3000. Tiles are 64 × 64 pixels (about 640 m).

## First-guess map
ESA WorldCover was used only as a hint for choosing tiles. It was not used as the label.

## Classes and counts (final labels)
| Class | Tiles |
|---|---|
| Industrial | 156 |
| Residential | 155 |
| SeaLake | 129 |
| HerbaceousVegetation | 90 |
| Forest | 81 |
| AnnualCrop | 69 |
| River | 37 |
| **Labelled total** | **717** |
| unsure (excluded) | 184 |

Class names follow EuroSAT. Highway, Pasture and PermanentCrop are not represented.

## Labelling and agreement
Two annotators labelled every tile: Person 1 and a second annotator (an AI, see `AI_USE.md`). Cohen's kappa is **0.853** on real classes only (515 tiles) and **0.567** with unsure counted as a label (901 tiles). Per-class agreement is highest for SeaLake, Industrial, Residential and AnnualCrop, and lowest for River (0.54) and Herbaceous (0.68). Rules and resolution are in `LABELLING_PROTOCOL.md` and `DISAGREEMENT_RESOLUTION.md`.

## Known limitations
- **Not a random sample.** Tiles were drawn in groups chosen from the map hint, so class counts do not reflect how common each class is.
- **Two scenes and two dates**, in different seasons (April and October), so results cannot be generalised to the whole country.
- **River is small** (37 tiles) and agreement is weak, because narrow rivers cover only part of a 640 m tile and look like vegetation. Results for River should be read with care.
- **Herbaceous vs Forest is ambiguous** at 10 m.
- **Labels come from looking at 10 m imagery**, with no field check or higher-resolution imagery.
- **One human annotator plus an AI second annotator.** The second annotator was not fully independent of Person 1 (see `AI_USE.md`).
- **Industrial** was defined broadly (large roofs, plants), and some airport aprons are labelled Industrial.
- **20.4% of tiles are unsure** and excluded, so the labelled set favours tiles that are easy to call.

## Licence and sources
Sentinel-2 data are free and open (Copernicus). ESA WorldCover is released under CC BY 4.0. Please credit both when sharing. Check the group's own licence before publishing the labels.

## Files
`labels_all.csv` (901 rows: `tile_file`, `region`, `group`, `person1`, `claude`, `final`, `resolution`), `counts_by_class.csv`, `disagreements.csv`, and `example_tiles.png` (six example tiles per class).
