# Cohort Thresholding and Contribution Bounding Tool

- **Focus area:** Disassociability  
- **Category:** Tool  
- **Status:** Example / reference implementation  
- **Author:** Anqi Zhou  

This tool demonstrates two foundational disassociability techniques used
in privacy-preserving analytics:

1. **Contribution bounding** – limiting how many times a single user can
   contribute to a cohort.
2. **Cohort thresholding** – only reporting cohorts that meet a minimum
   *k* number of bounded contributions.

These techniques are widely used in privacy-aware reporting systems
(e.g., advertising measurement, recommendation systems, event analytics).

---

## 1. What the Tool Does

Given an input CSV of event-level records:

- `(user_id, cohort_id, value)`

the tool:

1. Applies per-user-per-cohort **contribution bounds**  
   (default: each user contributes at most 1 event per cohort)

2. Applies **k-thresholding**  
   (default: cohort must have ≥ 5 bounded events)

3. Produces aggregated metrics:

- `cohort_id`
- `num_events`
- `sum_value`

---

## 2. Input Format

Expected CSV format:

```csv
user_id,cohort_id,value
