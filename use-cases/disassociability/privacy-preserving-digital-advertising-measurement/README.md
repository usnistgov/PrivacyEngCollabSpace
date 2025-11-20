- [Privacy-Preserving Digital Advertising Measurement with Differential Privacy](privacy-preserving-digital-advertising-measurement/README.md) – Use case describing disassociability and differential privacy techniques for privacy-preserving advertising measurement.

# Privacy-Preserving Digital Advertising Measurement with Differential Privacy

## Summary

- **Focus area:** Disassociability
- **Category:** Use Case
- **Status:** Prototype / in limited deployment
- **Primary contact:** [Anqi Zhou] ([Data scientist focusing on data anonymization & PETs])
- **Keywords:** differential privacy, synthetic cohorts, online advertising, attribution, privacy-preserving measurement

## 1. Context and Goals

This use case describes how an online advertising platform can use
disassociability techniques to measure the effectiveness of ads while
reducing the risk of re-identification of individuals and protected
groups.

The goals are:

1. Provide statistically useful metrics for advertisers (e.g., reach,
   conversions, return on ad spend).
2. Limit the risk that any single person or small group can be
   re-identified or profiled from measurement outputs.
3. Support regulatory and policy requirements around data minimization,
   purpose limitation, and privacy protections.

Although the example is motivated by large-scale digital advertising
platforms, the same approach can be applied to other domains where
event-level behavioral data is aggregated for analytics.

## 2. Data and Actors

**Data sources**

- Event-level logs of ad impressions and clicks.
- Event-level logs of conversions (e.g., purchases or sign-ups).
- Optional metadata about devices, browsers, or contexts.

The use case assumes that identifiers (e.g., user IDs, device IDs) are
available inside a secure processing environment but are not exposed in
final outputs.

**Actors**

- **Platform operator:** runs the data pipeline and enforces privacy
  protections.
- **Advertisers:** receive aggregated reports and dashboards.
- **End users:** individuals whose online behavior may be logged and
  included in aggregates.

## 3. Privacy Objectives and Risks

The platform wants to:

- Prevent re-identification of individuals from measurement outputs.
- Reduce the risk of inferring sensitive attributes about people or
  protected groups from aggregate reports.
- Limit linkability of the same individual across different campaigns
  or partners.

Key privacy risks include:

- Very small cohorts (e.g., one or a few users) receiving high spend
  or high value conversions.
- Combining granular breakdowns (e.g., by campaign, geo, device, and
  audience segment) that allow attackers to isolate individuals.
- Repeated measurements over time that can be differenced to recover
  contributions of a single person.

## 4. Disassociability Techniques Used

The use case combines several disassociability techniques:

1. **Aggregation and cohorting**

   - Events are grouped into cohorts defined by a limited set of
     dimensions (e.g., campaign, date, country, device type).
   - Audience segments and other fine-grained dimensions are mapped
     into coarser, privacy-aware buckets.

2. **Minimum thresholds and contribution limits**

   - Per-cohort minimum thresholds (e.g., at least *k* unique users)
     are enforced before reporting.
   - Per-user contribution limits prevent any single person from
     dominating a metric (e.g., a per-user cap on counted conversions
     per campaign).

3. **Differential privacy mechanisms**

   - For each eligible cohort, a differentially private mechanism
     (e.g., Laplace or Gaussian mechanism) is applied to counts and
     sums.
   - A global privacy budget is maintained across reports and time
     periods using a privacy accounting method (such as composition of
     DP events or a privacy loss distribution accountant).

4. **Synthetic cohorts or synthetic data (optional)**

   - For high-risk use cases, the platform may generate synthetic
     cohorts or synthetic event data that preserves key statistics
     while reducing linkage to real individuals.

These techniques are combined to reduce the attack surface while still
supporting useful aggregate reporting.

## 5. High-Level Workflow

1. **Ingest and preprocess logs**

   - Normalize event schemas and drop fields that are not needed for
     measurement.
   - Map identifiers to an internal representation scoped to the
     reporting context.

2. **Form cohorts**

   - Group events into cohorts based on allowed dimensions (e.g.,
     campaign, date, region).
   - Compute per-cohort aggregates (e.g., number of unique users,
     total impressions, total conversions, revenue).

3. **Apply contribution bounding**

   - Enforce per-user caps on contributions (e.g., maximum number of
     conversions per user per cohort).
   - Remove or down-weight cohorts dominated by very few users.

4. **Apply differential privacy**

   - Calibrate noise based on a global privacy budget and sensitivity
     of each metric.
   - Add random noise to aggregates to obtain DP-protected counts and
     sums.
   - Track cumulative privacy loss over time.

5. **Post-processing and reporting**

   - Suppress cohorts with high relative noise or low support.
   - Generate reports and dashboards with uncertainty annotations
     (e.g., confidence intervals or qualitative stability labels).

## 6. Example Metrics

Typical metrics supported by the DP measurement system include:

- DP-protected counts of impressions, clicks, and conversions.
- DP-protected revenues or conversion values.
- Ratios derived from noisy counts (e.g., click-through rate, 
  conversion rate), with care taken to avoid over-interpretation.
- Time-series aggregates (e.g., per-day counts) with privacy budget
  accounting across dates.

## 7. Implementation Notes

This use case can be implemented using existing open source
differential privacy libraries and accounting frameworks. Example
building blocks include:

- Differentially private primitives for counts and sums.
- Privacy accounting libraries to manage composition of privacy
  guarantees.
- Big data processing frameworks (e.g., batch or streaming) to handle
  large-scale logs.

The implementation should support:

- Configurable cohort definitions and thresholds.
- Configurable privacy budgets and mechanisms.
- Logging and audit trails for how privacy budgets are allocated and
  consumed.

## 8. Limitations and Trade-offs

- Stronger privacy guarantees (smaller epsilon, stricter thresholds)
  may reduce the utility of small campaigns and rare events.
- Repeated reporting over many dimensions and time periods consumes
  more privacy budget.
- Very small or highly targeted campaigns may not meet thresholds and
  will not receive detailed reporting.

These trade-offs should be documented and communicated to
stakeholders, including advertisers and internal decision-makers.

## 9. References and Related Work

- NIST Privacy Framework and Privacy Engineering Collaboration Space.
- Public documentation on differential privacy and synthetic data
  generation for statistical reporting.
- Academic and industry work on privacy-preserving measurement and
  attribution.

