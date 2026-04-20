# Hospital EHR De-Identification for Secondary Research Use

**Name of Use Case:** Hospital EHR De-Identification for Secondary Research Use

**Primary Focus Area (select one):** Disassociability

**Disassociability Keywords (select any relevant):** K-Anonymity, Anonymization, Information Leakage, Synthetic Data Generation

**Brief Description:** This use case describes how a hospital or health system can de-identify Electronic Health Record (EHR) data to enable secondary use for clinical research, public health reporting, and machine learning model development, while meeting HIPAA Privacy Rule requirements and minimizing re-identification risk for patients.

**Additional Notes:**
- Relevant regulatory frameworks: HIPAA Privacy Rule (45 CFR §164.514), Common Rule (45 CFR §46), NIST Privacy Framework
- Engages with the tension between data utility for research and patient privacy protection
- Community members can contribute alternative de-identification pipelines, utility benchmarks, or risk quantification approaches

**GitHub User Serving as POC (or Email Address):** @pw0607

**Affiliation/Organization(s) Contributing (if relevant):** Independent Researcher

## For A Hosted Use Case

**Context:**

1. A mid-to-large hospital or integrated health system (public or private sector) that maintains Electronic Health Records for its patient population. The organization has an internal research division or partners with external academic researchers.

2. The organization seeks to make patient data available for secondary purposes including clinical outcomes research, epidemiological studies, health equity analysis, and training machine learning models for clinical decision support, without exposing individual patient identities.

3. The data subject population includes all patients who have received care at the facility. Demographics span a broad range of ages, ethnicities, socioeconomic backgrounds, and geographic locations. Certain subpopulations (e.g., patients with rare diseases, small geographic areas) face elevated re-identification risk.

4. The privacy goal is to produce a de-identified dataset that satisfies HIPAA Safe Harbor or Expert Determination standards, such that the risk of re-identifying any individual patient is very low, while retaining sufficient clinical detail for meaningful research analysis.

5. Negative outcomes if the privacy goal is not met include:
   - Re-identification of patients, leading to disclosure of sensitive health conditions (e.g., HIV status, mental health diagnoses, substance use disorders)
   - Regulatory penalties under HIPAA (fines up to $1.5M per violation category per year)
   - Loss of patient trust and reputational harm to the institution
   - Potential discrimination against individuals based on disclosed health information

**Processing:**

6. Data processing lifecycle:
   - **Collection:** EHR data is collected during routine clinical care (diagnoses, procedures, lab results, medications, demographics, visit dates, provider notes).
   - **Storage:** Data resides in the hospital's EHR system (e.g., Epic, Cerner) in structured (HL7 FHIR, relational database) and unstructured (clinical notes) formats.
   - **De-identification:** Structured fields are transformed using generalization, suppression, and perturbation techniques. Unstructured text undergoes Named Entity Recognition (NER) to redact or replace PHI. Dates are shifted by a consistent random offset per patient.
   - **Analysis:** Researchers access the de-identified dataset through a secure research data warehouse.
   - **Disposal:** De-identified datasets are retained per the institution's data retention policy and securely deleted when no longer needed.

7. Yes. Detailed descriptions of data processing tasks and accuracy requirements can be provided, including acceptable generalization levels for diagnosis codes (e.g., ICD-10 3-digit vs. 5-digit), date precision (year vs. month vs. day), and geographic granularity (state vs. ZIP-3).

8. The organization intends to make de-identified datasets available to approved researchers through a data use agreement. Aggregate statistical results may be published in peer-reviewed journals. The organization may also release a synthetic version of the dataset publicly for broader research use.

9. Current privacy protections include:
   - Role-based access controls within the EHR system
   - HIPAA Safe Harbor de-identification applied manually by the research data team
   - IRB review for all research protocols involving patient data
   - Data use agreements with external research partners
   - Audit logging of all data access

10. Data:

    a. The dataset includes structured tabular data (CSV/Parquet exports from the EHR, typically 500K-5M patient records with 50-200 clinical variables) and unstructured clinical notes (free text, averaging 10-50 notes per patient). Total dataset sizes range from 10GB to 500GB depending on scope.

    b. The organization is willing to share synthetic data generated from the de-identified dataset with researchers. Real de-identified data would be shared only under a data use agreement with approved institutions.

**Solutions (for use cases with implemented solutions):**

11. Lessons learned:
    - Applying K-Anonymity (k=5) with generalization hierarchies for ICD-10 codes and ZIP codes provided a practical balance between privacy and utility for most research queries.
    - Synthetic data generation using differentially private methods (e.g., DP-CTGAN) proved effective for machine learning use cases where exact distributional fidelity was less critical.
    - Date shifting with a per-patient random offset preserved temporal relationships within a patient's record while preventing calendar-based re-identification.
    - Unstructured note de-identification using NER models required significant tuning to handle institution-specific terminology and abbreviations.

12. Challenges and limitations:
    - Rare disease patients and small geographic subpopulations required aggressive suppression, reducing utility for studies focused on those groups.
    - Utility measurement remains subjective; different research questions tolerate different levels of information loss.
    - Unstructured text de-identification is imperfect; residual PHI leakage in clinical notes remains a risk requiring manual review for high-sensitivity datasets.
    - Longitudinal data linkage across de-identified datasets is difficult without a consistent pseudonymous identifier, which itself introduces re-identification risk.
