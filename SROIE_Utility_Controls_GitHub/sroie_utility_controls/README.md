# SROIE utility controls — Sections 4.8–4.9, Tables 12–13

This package includes archived, text-free exact-match scores for the 350-document source control (1,050 condition records) and task-field ablation (807 records). Source control conditions are SOURCE_UNAUGMENTED, AUGMENTED_UNMASKED, and MASKED_SHARED. Ablation contains 350 baselines and company/date/address/total subsets of 252/63/16/126 documents.

## Recalculate reported results
Install numpy and pandas, then run `python reproduce.py`. Outputs are written to `regenerated/`. Bootstrap uses 10,000 paired document resamples, seed 20261003, with archived document order preserved. Exact-match indicators are retained; ground-truth strings, predicted strings, raw decoder text, and source images are omitted. Consequently this package supports aggregate recalculation but not independent rescoring of decoder strings.

## Rerun model inference
The original Colab notebooks are included as reference workflows. They require separately obtained source/augmented archives, synthetic metadata, and conservative C2 rendered inputs, with hashes recorded in run-spec files. These inputs are NOT bundled here. Paths must be adapted to the user's Drive. Model revision is pinned in the notebooks. The source control is a shared-mask experiment, not evidence of Risk-adaptive superiority. The field ablation is not a uniform PII-category test and has no equal-area irrelevant-content control. Field eligibility uses unique exact transcript matches, not model-output selection.

Manifest coordinates, source checks, and numerical run specifications are included. Source documents/full text are not redistributed. Original notebooks contain Korean interface instructions. No new inference was run in assembling this package.
