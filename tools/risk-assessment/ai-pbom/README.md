# AI PBOM — AI Privacy Posture & Data Map

**Primary Focus Area:** Privacy Risk Assessment

**Brief Description:** AI PBOM is a local-first, read-only CLI that inventories AI-related data assets (tables, vector
stores, prompt logs, training data, transcripts, and files), detects PII, credentials, and sensitive domain content
within them, and maps those assets to the AI applications that consume them via declared dependencies. It computes an
additive, explainable risk score (0-100) per asset and per application, with every score traceable to its contributing
findings, and outputs a structured Privacy/AI Bill of Materials (PBOM) as JSON plus a human-readable Markdown report.
The tool never modifies source systems and bounds all sampling to keep scans predictable on large data stores.

**Tool Link:** https://github.com/k-nithin/ai-pbom

**Additional Info:**
* Paper: [AI Privacy Posture & Data Map: A Threat Model and Additive Risk Scoring Framework](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=6840119) (SSRN) — formalizes the T1-T4 threat model, 8-dimension gap analysis, and scoring model the tool implements.
* Use Cases:
    * Build and maintain an inventory of AI-specific data assets (vector tables, prompt logs, training data, transcripts) that general data-discovery tools don't model as first-class asset types.
    * Detect pgvector-backed vector stores and PII/secrets/sensitive-domain content within them before they're wired into an AI application.
    * Trace which AI applications depend on which underlying data assets, so a risk finding on an asset is attributable to the application(s) it affects.
    * Produce an explainable, additive risk score per asset/application with traceable drivers, suitable for privacy office or AI governance review.
    * Generate a PBOM (JSON) and Markdown report for audit trails, without exposing raw PII in the output.
* Supported data sources: Postgres, pgvector, and filesystem connectors, with a pluggable connector/detector interface for adding more.
* Quick start / self-contained demo (no database required) and a Docker-based Postgres + pgvector demo are documented in the repo README.
* License: Apache 2.0.

**GitHub User Serving as POC (or Email Address):** @k-nithin

**Affiliation/Organization(s) Contributing (if relevant):** Independent / none
