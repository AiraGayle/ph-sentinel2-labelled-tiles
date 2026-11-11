# Decision Log: Philippine Target Set (Member 2)

CMSC 178 IP, Group 4, Track A (EuroSAT to Philippines). Last updated Nov 11, 2026.
Items marked **(verify)** are not confirmed yet.

## 1. What this task must deliver (from the primer)

- At least 6 classes shared with EuroSAT, at least 150 tiles per class, from at least 2 regions.
- 64 x 64 tiles at 10 m, cut from cloud-screened Sentinel-2 L2A scenes, same bands as EuroSAT.
- Labels: official land-cover map as first guess, then visual check by two annotators. Report Cohen's kappa (aim 0.7 or higher) and how disagreements were resolved.
- Data card: processing level and scaling vs EuroSAT, cloud tiles dropped, written label definitions, neighbouring-tile leakage.
- Release tiles, labels, scene metadata, tiling code and a datasheet.
- For the group: counts for slide 3 (Data) and slide 8 (Risks).

## 2. Decisions

| # | Date | Decision | Reason |
|---|------|----------|--------|
| 1 | Nov 4 | Regions: Metro Cebu (`CEB`) and Central Luzon (`CLZ`: Pampanga/Bulacan) | Cebu is home area; Luzon adds rice, wide rivers, forest |
| 2 | Nov 4 | Region 3 (Davao/Bukidnon) optional, only if time allows | Strengthens "between regions" claim |
| 3 | Nov 4 | Drop Highway, Pasture | Highway narrower than 10 m; Pasture overlaps crops and grass. (HerbaceousVegetation brought back, see #14) |
| 4 | Nov 4 | Core classes: Forest, Residential, Industrial, River, SeaLake, AnnualCrop | Meets the minimum of 6 |
| 5 | Nov 4 | PermanentCrop kept as provisional | Coconut can look like forest at 10 m; drop if class kappa is below 0.7 |
| 6 | Nov 4 | Fishponds count as SeaLake | Open water. Tag them in a `subtype` column and note as a limitation |
| 7 | Nov 4 | One L2A scene per region; Metro Cebu scope only, tiles cut from the whole scene | About 900 labelled tiles needed; scene holds far more. Limitation: not all of Cebu Island |
| 8 | Nov 9 | Use RGB only (B04, B03, B02) | Baseline first; other bands only if needed |
| 9 | Nov 10 | Subtract the L2A reflectance offset (-1000, read from scene metadata) | N05.12 and N05.13 are post-2022 baselines; EuroSAT has no offset |
| 10 | Nov 10 | Use stretch 0 to 3000 (to 8-bit), same for every scene | Confirmed: Member 1's EuroSAT PNGs use `lo=0, hi=3000` on bands (3, 2, 1) |
| 11 | Nov 10 | Tiles: 64 x 64, non-overlapping; drop any tile with cloud, shadow, cirrus, saturated/defective or no-data pixels (SCL classes 0, 1, 3, 8, 9, 10) | Avoids near-duplicates and cloudy tiles labelled as land |
| 12 | Nov 11 | Keep L2A and document that EuroSAT is top-of-atmosphere **(proposed, confirm with group)** | L1C download is slower and has no SCL layer; the difference goes in the data card and slide 8 |
| 13 | Nov 11 | Splitting Philippine tiles: split by region first; small blocks (about 2-5 km) only inside a region for the few-shot adaptation set **(proposed, confirm with Member 1)** | Member 1's 0.5 degree blocks are too big for a scene of about 0.2 degrees. Zero-shot needs no split |
| 14 | Nov 11 | Add HerbaceousVegetation back as a 7th class: grass, shrubs, brown scrub, grazing land (Pasture counts here) **(proposed, confirm with Member 1)** | Much of Cebu in dry season is scrub with no class, so many tiles were `unsure`. Drop again if its kappa is below 0.7. Merge EuroSAT Pasture + Herbaceous predictions when evaluating |

## 3. Scenes (both downloaded and unzipped in `scenes/`)

| Field | `CEB` | `CLZ` |
|-------|-------|-------|
| Folder | `Cebu.SAFE` | `Central Luzon (Pampanga and Bulacan).SAFE` |
| Sensing date | 2026-04-25 | **2026-10-15** |
| Tile ID | 51PWM | 51PTS |
| Processing baseline | N05.12 | N05.13 |
| Whole-scene cloud | 8.48% | not recorded yet |
| Season | Dry | **Wet** |

- The Luzon scene is wet season, unlike the planned Feb-Apr. Expect more cloud, and Cebu vs Luzon now differs in season as well as place. Limitation for slide 8. If too many tiles are lost to cloud, get a Feb-Apr scene of 51PTS.
- **(verify)** 51PWM covers the east side of Metro Cebu (Mandaue, Lapu-Lapu); if not, add tile 51PXM.
- **(verify)** 51PTS covers both Pampanga and Bulacan.

### 3b. Tile counts (unlabelled candidates, 64 x 64, max-cloud 0, offset -1000, stretch 0-3000)

| | `CEB` (51PWM) | `CLZ` (51PTS) |
|---|---|---|
| Grid tiles in scene | 29,241 | 29,241 |
| Dropped: cloud/shadow/cirrus/bad pixels | 5,710 (19.5%) | 6,634 (22.7%) |
| Dropped: no-data (scene edge) | 2,589 (8.9%) | 0 |
| **Kept** | **20,942** | **22,607** |
| Labelled so far | 0 | 0 |

Kept plus dropped equals grid total for both scenes. Labelled counts per class are still to do.

## 4. Classes (draft definitions)

| Class | Counts as | Not |
|-------|-----------|-----|
| Forest | Dense natural tree cover, incl. mangrove | Coconut or plantations; scattered trees |
| Residential | Mostly houses, small streets, yards | Single building in farmland; factories |
| Industrial | Large roofs, factories, warehouses, port yards | Houses; small shops in neighbourhoods |
| River | Visible river channel crossing the tile | Creeks under about 20 m; lakes; sea |
| SeaLake | Tile mostly open water: sea, lake, reservoir, fishpond | River channels |
| AnnualCrop | Rice, corn, vegetables (replanted each year) | Coconut, banana, orchards, fallow grass |
| PermanentCrop (provisional) | Coconut, banana, mango in rows | Keep only if separable from Forest |
| HerbaceousVegetation | Grass, shrubs, brown or green scrub, grazing land | Field edges (AnnualCrop), dense trees (Forest). Smooth texture, no straight edges |

Mixed tiles: label by the dominant class (more than 50%); otherwise `unsure` and exclude.

## 5. Tools and method

- `g4_cut_tiles.py`: one scene in, PNG tiles + metadata CSV (scene, row, col, UTM and lat/lon, date, cloud fraction, empty label columns) + summary JSON out. It prints baseline, offset, date, tile ID. Run once per scene.
- `g4_contact_sheets.py`: picks a seeded random sample from the CSV and makes numbered 6 x 6 sheets plus `label_sheet.csv` to fill in. The second annotator uses the same `--seed`.
- Labelling rules: label from the pictures and the reference map, never from model predictions. Second annotator labels a random subset blind.
- Class names must match EuroSAT exactly: `AnnualCrop`, `Forest`, `HerbaceousVegetation`, `Industrial`, `PermanentCrop`, `Residential`, `River`, `SeaLake`.

## 6. Status and to-do

| Item | Status |
|------|--------|
| Regions, classes, definitions | Done |
| Scenes downloaded and unzipped | Done |
| Stretch and offset confirmed | Done |
| Cut tiles (CEB, CLZ) | Done Nov 11 (counts in section 3b) |
| Check tiles by eye; record counts and drops | To do |
| Reference land-cover map (CopPhil / NAMRIA; ESA WorldCover as fallback), mapping table to our classes | To do. Check licence; do not redistribute |
| Second annotator | **Not found yet** |
| Sample about 150 per class (River and Industrial scarce in Cebu) | To do |
| Label, then compute kappa | To do |
| Send counts and metadata CSV to Members 1 and 5 | To do |

## 7. Limitations to report

- EuroSAT is top-of-atmosphere; Philippine tiles are L2A surface reflectance.
- One scene per region, one date each; Cebu is dry season, Luzon is wet season.
- Metro Cebu only, not all of Cebu Island.
- Fishponds counted as SeaLake; PermanentCrop vs Forest is hard at 10 m; Pasture is merged into HerbaceousVegetation.
- Tile counts for some classes may be below 150; state the actual numbers.
