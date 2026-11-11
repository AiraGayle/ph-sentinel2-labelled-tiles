# AI use

An AI assistant (Claude, by Anthropic) was used in this part of the project. This file records what it did.

## Tools and scripts
- The AI helped write the helper scripts (`g4_cut_tiles.py`, `g4_prelabel.py`, `g4_targeted_sheets.py`, `g4_label_page.py`, `g4_kappa.py`, `g4_package_B.py`) used to cut tiles, attach the map hint, build labelling sheets and compute kappa.

## Second annotator
- The AI acted as the **second annotator** because no second person was available. It labelled tiles by looking at the images, without the map hint.
- It labelled in stages: 120 shared tiles first, then all 580 tiles of the first two batches, then the 237 tiles of the third batch and the 84 tiles of the fourth batch.
- **Independence is limited.** The AI had earlier reviewed Person 1's first batch and suggested corrections, and Person 1's labels for the third and fourth batches were visible to it when it labelled them. The AI labelled from the images, but the two sets of labels are not fully independent, so the kappa values may be somewhat optimistic.
- After the first comparison, Person 1 supplied a broader rule for Industrial. The AI re-checked its Industrial labels against that rule and its labels were revised. The kappa before the revision (0.50 with unsure, 0.85 classes only) and after (0.55 and 0.84) are both reported.

## Review and resolution
- The AI reviewed Person 1's first batch against the images and proposed corrections (56 clear and 60 suggested). Person 1 decided whether to use them. The original labels are kept unchanged in `person1`.
- The AI applied the resolution rules in `DISAGREEMENT_RESOLUTION.md` to produce the `final` column. This was not a discussion between two humans.

## Documents
- The AI drafted the labelling protocol, data card and disagreement summary from the numbers in the labels file. Person 1 should read and edit them before submission.

## What was not done by the AI
- Person 1 made all original labels, chose the classes and the Industrial rule, and decides what is submitted.
