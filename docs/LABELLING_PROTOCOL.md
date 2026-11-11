# Labelling protocol — Philippine Sentinel-2 tile set (Track A)

## Purpose
Build a small, documented, labelled set of Philippine Sentinel-2 tiles to test a model trained on EuroSAT (European imagery). The labels are the reference the model is scored against, so the protocol is written to make them as consistent as possible.

## Data being labelled
- Sentinel-2 L2A, true colour (B04, B03, B02), 10 m pixels.
- Tiles are 64 × 64 pixels (about 640 m × 640 m), shown with a fixed contrast stretch (0–3000) so tiles look consistent.
- Two scenes: **CEB** (tile T51PWM, Cebu, 2026-04-25) and **CLZ** (tile T51PTS, Luzon, 2026-10-15).
- 901 tiles were labelled. They were not drawn at random (see "Sampling").

## First guess from a land-cover map
An official land-cover map (ESA WorldCover) was overlaid on each tile and used **only as a hint** to choose which tiles to show (for example "mostly built-up", "mostly water", "mostly forest"). The map was never used as the label. Annotators decide from the image.

## Sampling
Tiles were drawn in groups based on the map hint so that rarer classes (Industrial, River) would be represented: Narrow-water candidates (285), Industrial candidates (180), Forest (112), Built-up (108), Annual crop (72), Open water (72), Grass/scrub (72). Because of this, class counts in the set do **not** reflect how common each class is in the Philippines.

## Classes (EuroSAT names)
| Class | Use when the tile is mainly… |
|---|---|
| Forest | continuous dark tree canopy |
| HerbaceousVegetation | grass, shrub or open vegetation, with lighter green or brown texture and bare patches |
| AnnualCrop | a mosaic of rectangular field parcels (cropland) |
| Residential | dense small roofs and streets |
| Industrial | large roofs, large manufacturing or plant spaces (see rule below) |
| River | a winding river band with banks crossing the tile |
| SeaLake | open water: sea, bays, lakes, fishponds |
| unsure | no class is clearly dominant |

EuroSAT classes **not used**: Highway, Pasture, PermanentCrop. They were not targeted by the sampling, so they are not represented here.

## Main rule
Label the class that covers **more than half** of the tile. If no class clearly does, or the two annotators cannot settle it, label **unsure**. Unsure tiles are excluded from the labelled set that is used to score the model.

## Specific rules
1. **Industrial.** A tile counts as Industrial if it includes spaces with large roofs or large spaces for manufacturing or plants (warehouses, factories, tank farms, ports and similar). Small roofs in a regular grid are Residential. *Known limit:* some airport aprons were also labelled Industrial, which is a judgement call.
2. **River vs SeaLake.** River is a winding band of water with banks. Open water, bays, coast and fishponds are SeaLake. A thin river that covers only a small part of the tile is not River.
3. **Herbaceous vs Forest.** Forest is dark, continuous canopy. Herbaceous is lighter grass, shrub or open vegetation. This boundary is hard at 10 m and is the main source of disagreement.
4. **Fishponds** (dark rectangular grids) are SeaLake.
5. **Clouds, haze or sensor artefacts** covering the tile: label unsure.

## Process
1. Person 1 labelled all tiles from the image, with the map hint visible.
2. A second annotator (an AI, see `AI_USE.md`) labelled all tiles from the image.
3. Agreement was measured with Cohen's kappa on Person 1's original labels against the second annotator's labels (never on the resolved labels).
4. Disagreements were resolved with the rules in `DISAGREEMENT_RESOLUTION.md` and written to a `final` column.
5. The Industrial rule above was refined after the first comparison; the second annotator's Industrial labels were revised to follow it. The result is reported as agreement after a guideline revision.

## Files
`labels_all.csv` has one row per tile: `person1` (original labels), `claude` (second annotator), `final` (resolved label), `resolution` (how it was decided).
