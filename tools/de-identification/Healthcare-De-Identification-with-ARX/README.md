# Healthcare De-Identification with ARX

**Name of Tool:** Healthcare De-Identification with ARX

**Primary Focus Area (select one):** Disassociability

**Disassociability Keywords (select any relevant):** K-Anonymity, Anonymization, Information Leakage

**Brief Description:** A configuration guide and workflow for applying the ARX Data Anonymization Tool to healthcare datasets in compliance with the HIPAA Privacy Rule's Safe Harbor and Expert Determination de-identification standards (45 CFR §164.514). This contribution provides pre-built anonymization configurations for common healthcare data elements (e.g., diagnosis codes, dates of service, geographic data, age) and demonstrates how to apply K-Anonymity, L-Diversity, and T-Closeness models to Electronic Health Records (EHR) while preserving analytical utility for research purposes.

**Additional Notes:**
- Covers both HIPAA Safe Harbor (removal of 18 identifier types) and Expert Determination methods
- Includes sample transformation rules for ICD-10 code generalization hierarchies
- Provides utility metrics for measuring information loss after anonymization
- Compatible with common EHR export formats (CSV, HL7 FHIR JSON)
- Related NIST resource: NIST SP 800-188, De-Identifying Government Datasets

**GitHub User Serving as POC (or Email Address):** @pw0607

**Affiliation/Organization(s) Contributing (if relevant):** Independent Researcher

## For a Linked Tool

**Tool Link:** [https://arx.deidentifier.org](https://arx.deidentifier.org)
