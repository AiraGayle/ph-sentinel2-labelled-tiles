# Labelling protocol — Philippine Sentinel-2 tile set (Track A)

## Purpose
Build a small, documented, labelled set of Philippine Sentinel-2 tiles to test a model trained on EuroSAT (European imagery). The labels are the reference the model is scored against, so the protocol is written to make them as consistent as possible.

## Data being labelled
- Sentinel-2 L2A, true colour (B04, B03, B02), 10 m pixels.
- Tiles are 64 × 64 pixels (about 640 m × 640 m), shown with a fixed contrast stretch (0–3000).
- Two scenes: **CEB** (T51PWM, Cebu, 2026-04-25) and **CLZ** (T51PTS, Luzon, 2026-10-15).
- 901 tiles were examined (not drawn at random, see "Sampling").

## First guess from a land-cover map
ESA WorldCover was overlaid on each tile and used **only as a hint** to choose which tiles to show. It was never the label. Annotators decide from the image.

## Sampling
Tiles were drawn in groups based on the map hint so rarer classes (Industrial, River) would be represented: Narrow-water candidates (285), Industrial candidates (180), Forest (112), Built-up (108), Annual crop (72), Open water (72), Grass/scrub (72). Class counts therefore do **not** reflect how common each class is in the Philippines.

## Class definitions (EuroSAT names)
These describe how Person 1 labelled. Each tile gets the one class that covers more than half of it.

**Forest** — mostly trees. Dark green, continuous, fine-textured canopy with few bare patches. Not lighter grass/scrub (HerbaceousVegetation) and not neat rectangular fields (AnnualCrop).

**HerbaceousVegetation** — mostly grass, shrub or other low natural vegetation. Lighter green or green-brown, patchy or streaky, bare soil often showing, no regular field edges. Not dark continuous canopy (Forest). The Forest/Herbaceous boundary is the hardest call in this set.

**AnnualCrop** — farmland. A mosaic of rectangular or strip-shaped parcels in different greens and browns, with straight edges and farm tracks (e.g. rice, vegetables). Not irregular natural vegetation, and not flooded fishponds (SeaLake).

**Residential** — mostly housing. A dense speckle of small roofs (red, grey, blue, white) along streets, with trees between. A few larger buildings among many small roofs is still Residential.

**Industrial** — built-up land dominated by large buildings rather than houses. Large bright or coloured flat roofs, warehouses, factories, big rectangular buildings, yards and wide roads, usually with fewer trees than Residential. In Person 1's labels this includes industrial estates, port and logistics areas, and some airport aprons (a judgement call). Not small roofs in a regular pattern (Residential).

**River** — a winding band of water with banks that crosses the tile, including wide muddy rivers and braided riverbeds. Elongated brown, green or grey band, often with vegetation or settlements on both sides. Not open water such as bays and the coast (SeaLake), and not a thin stream covering only a small part of the tile.

**SeaLake** — a large body of standing water: sea, bay, lake or reservoir. In this set it also includes fishponds and flooded pond grids (dark rectangular grids with thin embankments). Smooth dark blue, grey or green with little texture. Not a narrow winding band with banks (River).

**unsure** — no class covers more than half the tile, or it is too mixed, hazy or cloudy to call. Unsure tiles stay in the file but are excluded from scoring.

EuroSAT classes **not used**: Highway, Pasture, PermanentCrop (not targeted by the sampling).

## Main rule
Label the class that covers **more than half** of the tile; otherwise **unsure**. Clouds, haze or sensor artefacts covering the tile are also **unsure**.

## Process
1. Person 1 labelled all tiles from the image, with the map hint visible.
2. A second annotator (an AI, see `AI_USE.md`) labelled all tiles from the image.
3. Agreement was measured with Cohen's kappa on Person 1's original labels against the second annotator's labels (never on the resolved labels).
4. Disagreements were resolved with the rules in `DISAGREEMENT_RESOLUTION.md` and written to a `final` column.

## Files
`labels_all.csv` has one row per tile: `person1` (original labels), `claude` (second annotator), `final` (resolved label), `resolution` (how it was decided).
