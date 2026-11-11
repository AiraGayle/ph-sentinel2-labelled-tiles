# How disagreements were resolved

## Agreement (Cohen's kappa)
Kappa compares Person 1's original labels with the second annotator's labels on the same 901 tiles:

κ = (p_o − p_e) / (1 − p_e), where p_o is the share of tiles with the same label and p_e is the agreement expected by chance (for each class, multiply the two annotators' shares of that class, then add up).

| Version | Tiles | Raw agreement | Kappa |
|---|---|---|---|
| Real classes only (unsure excluded) | 515 | 0.878 | **0.853** |
| Unsure counted as its own label | 901 | 0.632 | **0.567** (target ≥ 0.70) |

Agreement per class (share of Person 1's tiles where the second annotator agreed): SeaLake 0.98, AnnualCrop 0.95, Residential 0.94, Industrial 0.93, Forest 0.90, Herbaceous 0.68, River 0.54.

The 0.853 figure describes the tiles that go into the labelled set. The 0.567 figure is lower mostly because the second annotator used "unsure" much more often than Person 1 (335 vs 168 tiles). River and Herbaceous are the least reliable classes: River tiles were often called SeaLake, and Herbaceous tiles were often called Forest.

An earlier comparison, before the Industrial rule was refined, gave kappa 0.50 (unsure as a label) and 0.85 (classes only).

## Resolution rules
The two annotators disagreed on **332 of 901 tiles**. The `final` label was set as follows (the rule applied to each tile is in the `resolution` column of `labels_all.csv`; the per-tile list is in `disagreements.csv`):

| Rule (`resolution`) | Tiles | What it means |
|---|---|---|
| accepted_person1 | 118 | One annotator gave a class, the other said unsure. The class was kept. |
| industrial_rule | 56 | The tile includes large roofs or plant spaces, so it is Industrial under the Industrial rule. |
| unsure | 49 | Neither annotator could settle it, or a re-check showed no class covered more than half the tile. Left out of the labelled set. |
| accepted_claude | 38 | Person 1 said unsure and the second annotator gave a class. That class was kept. |
| conflict_old_review | 30 | Different real classes. An earlier image review of those tiles was used. |
| rechecked | 26 | Industrial or River tiles re-checked against the image and the map. Kept as that class only where it clearly dominated, otherwise unsure. |
| conflict_claude | 15 | Different real classes. The second annotator's image call was used, supported by the map hint. |

Tiles where both annotators agreed (569 of 901) kept their label.

## Notes
- Kappa is always computed from the original `person1` and `claude` columns, never from `final`.
- Resolution was applied by rules, not by discussion between two humans (see `AI_USE.md`). Person 1 should re-check the 30 + 15 tiles where the annotators picked different real classes if time allows.
- `final` contains 717 labelled tiles and 184 unsure tiles.
