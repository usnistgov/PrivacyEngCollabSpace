
# STRM Privacy Diagnostics

**Primary Focus Area:** Privacy Risk Assessment

**Tool Link:** https://github.com/strmprivacy/strm-privacy-diagnostics/

**Brief Description:**  STRM Privacy Diagnostics is a simple Python package to quickly run privacy metrics on your data. Obtain the K-anonimity, L-diversity and T-closeness to asses how anonymous your data is (pre- or post processing), and how it's balanced with data usability. Privacy Diagnostics is intented as an extension to the STRM platform, which allows you to collaborate with stakeholders on setting policy to data (using a **data contract**) and applying the transformations to dedicated sinks with the contract as machine-interpretable instruction.

**Additional Notes:** 
- An [A - Z demo notebook](https://deepnote.com/workspace/STRM-demos-2614c69d-1aae-4c75-a0b8-ee631006da30/project/Data-team-in-a-day-with-STRM-eb9f78ee-b796-48e5-b1ff-b77815a3952a/notebook/Anonymisation%20pipelines%20with%20STRM%20Privacy-681be7708cf844589c24db36e0a5d2d9) of using STRM and leveraging Privacy Diagnostics to measure anonymity.
- [STRM documentation](https://docs.strmprivacy.io/docs/latest/overview)
- [STRM open sourced repos](https://github.com/strmprivacy)
- Example uses:
    - **TST as PRD**. Assess if your production data is sufficiently anonymized to be safely used as test data.
    - **Auditing**. Test (or prove!) your data is truly anonymous (for instance, in the context of GDPR recital 26).
    - **Data sharing**. Protect user privacy and confidentiality and ensure your data is properly anonymized before sharing data with third parties (like vendors, the statistical bureau, etc).
    - **Machine learning and AI**. Test if your training data is properly anonymized so you don't inadvertently include sensitive user information (bonus: implement the package as a pre-training evaluation step in your code or use it in CI/CD).
    - **Happy compliance folks**. Drop the endless explaining to your compliance team, just show and prove your data is safe to use.

**GitHub User Serving as POC:** @[astronomous]

**Keywords:** Differential Privacy, K-Anonymity, Anonymization, Information Leakage, Algorithmic Fairness, Machine Learning, Pseudonimization, Data Usability