# Supplementary validation for risk-adaptive OCR masking

Repository prepared for electronics-4530594. This package contains a NEW conservative C2 supplementary experiment and a controlled policy-scenario audit. It does not reproduce historical Table 6, provide calibrated linkage/rarity assessment, or establish end-to-end privacy protection.

## Completed measurements
Official SROIE test split: 350 augmented documents, 846 inserted PII entities, 26 negative-control documents. The original 35-document selection is retained; all remaining 315 test documents are added, with no performance-based filtering. Full black masks use half-open annotation boxes and zero margin. Strong and Risk-adaptive are identical in this setting. Full annotation coverage; mean masked page area 1.237651%; area saving zero.
Tesseract 5.3.4 eng PSM7 complete normalized value recovery: original 638/846, masked 0/846. Donut philschmid/donut-base-sroie revision 51e72e5d160efa472ee3958d79a766faa42f6c5d: normalized four-field exact match original 61.142857%, masked 62.714286%; paired difference +1.571429 pp, bootstrap CI +0.642857 to +2.571429 pp. Model originally resolved at execution; revision is recorded for subsequent reproduction.

## Run coordinate and context checks without document images
```
pip install numpy pillow
python output/sroie_current_policy/evaluate_current_policy.py --annotations output/sroie_current_policy/annotations_test350.zip --selection output/sroie_current_policy/original35_selection.csv --out reproduced_coordinate_results
python context_policy_audit.py
python verify_public_utility.py
```
The context audit covers 18 types x 3 contexts x 7 supplied assessment scenarios = 378 decisions. Scenario judgments are fixtures, not estimated population risks. It checks protective precedence, incomplete/conflicting assessment behavior, and G2 context effects. It does not substantiate G3 empirical preservation benefits; with the same favorable supplied assessment, G3 decisions are identical across contexts. No new numerical rarity/linkage threshold is claimed.

## Render and OCR with locally obtained inputs
Place the author's PII-augmented official test archive at `ocr_images/SROIE-PII-full971-images-test.zip` and the author's full metadata archive at `ocr_metadata/SROIE-PII-full971-metadata.zip` under the package root. These are augmented author inputs, not interchangeable with unaugmented SROIE source files. Install Tesseract 5.3.4 with eng and Python dependencies, then:
```
python output/render_sroie_current.py
python output/audit_current_ocr.py
```
Rendering produces `output/SROIE_Current_C2_Rendered350.zip`. Full metadata includes target strings required for OCR scoring. The released coordinate annotations omit these strings. Source images and full metadata are not redistributed in this package; coordinate and metric checks are self-contained, full image inference is not.

## Donut
Open SROIE_Current_C2_Donut350.ipynb in Colab. Follow its input and Drive-folder instructions with the original augmented image zip, rendered image zip, and full metadata zip. It performs 700 inferences (350 original plus 350 shared masked), no training or tuning, and a paired document bootstrap (10,000 replicates; seed 20261003). Predictions in public_utility_scores.csv are numeric field indicators only. verify_public_utility.py reproduces aggregate utility and bootstrap CI; it does not recheck predicted text against ground truth.

## Annotation provenance and limitations
Coordinates are insertion-derived ground truth from existing author augmentation records. This release does not include the historical synthetic-value generator, its seed, manual-review protocol, or historical primary experiment evaluator. Those details must not be inferred from this new audit. Unannotated source content remains visible. OCR results concern full synthetic values, not partial recovery or real-person re-identification. No C1/C3 document inference or original-unaugmented control was performed.

## Scope of release
Author-written evaluation scripts, derivative coordinate records, selection IDs, numeric score records, aggregate results, and notebook. Third-party source licenses remain applicable. No source images, manuscript, synthetic text values, OCR strings, or receipt ground-truth strings are included. No assertion that the full historical experiment is reproducible from this package.

## SROIE coverage reanalysis
The sroie35_category_reanalysis directory contains coordinate annotations, entity-level scores, aggregate results, and reproduction code for the revised SROIE row in Table 6 and Tables 17–18. This analysis uses the original 35-document external-validation sample and is distinct from the archived OCR pilot and the supplementary conservative 350-document experiment.
