# Privado Scan

**Primary Focus Area:** Privacy Risk Assessment

**Brief Description:** Privado Scan is an open-source privacy scanner that allows an engineer to scan their application 
code and discover how data flows in the application. It detects hundreds of personal data elements being processed and 
further maps the data flow from the point of collection to "sinks" such as external third parties, databases, logs, and 
internal APIs. It allows privacy engineers to concretely verify and assess if a certain data collection policy set on an 
application actualy matches the implementation right in the code itself - thus embedding privacy assesments in the
developers' workflow.

**Tool Link:** https://github.com/Privado-Inc/privado
 
**Additional Info:** Here are some resources to learn how Privado Scan works and how to contribute to it:
 * Source: [Rules](https://github.com/Privado-Inc/privado), [Engine](https://github.com/Privado-Inc/privado-core)
 * Docs: https://docs.privado.ai
 * Use Cases:
    * Generate and maintain data maps and Record of Processing Activity (RoPA) Reports by scanning code
    * Discover and classify personal data elements inside the application's code and verify if they adhere to privacy policies
    * Get comprehensive insight on dataflows within an application from interesting sources (such as user input forms) to 
    interesting sinks (such as logs, external services, third parties, databases etc.) 
    * Verify and enforce data protection and governance policies right in code
    * Assess private data leakage risks by directly verifying it at an engineering level (eg. verify if a developer collected
    precise location in a phone app and if it was actualy sent to a remote third party logging service)
 * Talks/Videos: *Building an Automated Machine for Discovering Privacy Violations at Scale (Usenix Enigma 2023)* 
 [[Link]](https://www.usenix.org/conference/enigma2023/presentation/sharma)

Feedback and suggestions for improvement of Privado Scan are welcome. Please reach out to us on our 
[Privado Slack Community](https://join.slack.com/t/privado-community/shared_invite/zt-yk5zcxh3-gj8sS9w6SvL5lNYZLMbIpw)

**GitHub User Serving as POC (or Email Address):** @tuxology

**Affiliation/Organization(s) Contributing (if relevant):** Privado Inc.