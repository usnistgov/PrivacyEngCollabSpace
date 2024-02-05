# Privacy Engineering Collaboration Space
The NIST Privacy Engineering Collaboration Space is an online venue open to the public where practitioners can discover, share, discuss, and improve upon open source tools, solutions, and processes that support privacy engineering and risk management.

## Focus Areas
We have launched this space with an initial focus on disassociability and privacy risk assessment tools and use cases, and welcome [feedback](mailto:collabspace@nist.gov) on topics of interest from the community. 

* **Disassociability:** a technique or process applied to a dataset with the goal of preventing or limiting certain types of privacy risks to individuals, protected groups, and establishments, while still allowing for the production of aggregate statistics. This focus area includes a broad scope of disassociability to allow for noise-introducing techniques such as differential privacy, data masking, and the creation of synthetic datasets that are based on privacy-preserving models.

* **Privacy Risk Assessment:** a process that helps organizations to analyze and assess privacy risks for individuals arising from the processing of their data. This focus area includes, but is not limited to, risk models, risk assessment methodologies, and approaches to determining privacy risk factors. 

## Contribute to the Space 

Contributions come in three categories:

1. **Tool:** A tool can be an open source solution or process, ranging from software to frameworks. 
2. **Use Case:** A use case is an example of an organization processing data about individuals for some explicit purpose(s) (e.g., where a goal is to prevent re-identification of the data during its processing, improve privacy risk assessment practices).
3. **Feedback:** Help the community. Provide feedback on tools and use cases.

Tools and use cases are contributed via pull requests, while feedback is contributed via issues. Contributed tools and use cases can be hosted directly in this repository, or you can host them elsewhere online and link to them from this repository.

### How to Contribute Tools and Use Cases

1. Fork a copy of USNISTGOV/PrivacyEngCollabSpace to your own organizational or personal space. 

2. Create a branch in your fork, named specifically for your contribution. 

3. In your branch: 

	A. Create a new directory within the relevant tool or use case directory: tools/disassociability, tools/risk-assessment, use-cases/disassociability, or use-cases/risk-assessment. Example: *tools/disassociability/[your-contribution-name]*

	B. Name the directory to describe your contribution. 

	C. Include in the directory a README.md file that follows the relevant [template](https://github.com/usnistgov/PrivacyEngCollabSpace/tree/master/templates). There is a template for a [tool](https://github.com/usnistgov/PrivacyEngCollabSpace/tree/master/templates/tool-template.md) and for a [use case](https://github.com/usnistgov/PrivacyEngCollabSpace/tree/master/templates/use-case-template.md) contribution.

	D. If hosting a tool in this repository, also include in the directory any pertinent source code files or documentation. 

	E. Update the README.md file of the main directory to which you’re contributing. This README provides an index of that directory's contents. It should include an entry reflecting your contribution. 

5. Create a [pull request](https://github.com/usnistgov/PrivacyEngCollabSpace/pull/new/master) (PR) from your branch to the master branch in USNISTGOV/PrivacyEngCollabSpace. 

6. Moderators will then review the PR and may provide comments and suggestions to the contributor. 

### How to Contribute Feedback 

Submit an [issue](https://github.com/usnistgov/PrivacyEngCollabSpace/issues/new) to provide feedback on tools or use cases in the space. Please select appropriate tags related to the feedback. 

### Additional Contribution Resources

**GitHub Help:** If you're having trouble with these instructions, and need more information about GitHub, pull requests, and issues, visit GitHub's Help [page](https://help.github.com/categories/collaborating-with-issues-and-pull-requests/). 

**Contribution Assistance:** If you're having trouble submitting your contribution to this space, or otherwise would like to send us feedback, [contact us](mailto:collabspace@nist.gov). 

## Browse Tools and Use Cases

Interested in tools or use cases for disassociability and privacy risk assessment? **Browse the contributions [here](https://www.nist.gov/itl/applied-cybersecurity/privacy-engineering/collaboration-space/browse).**

## Operating Rules 

NIST will only accept open source submissions, per the Open Source Initiative’s [definition](https://opensource.org/osd) of “open source”. Upon submission, materials will be public, considered to be open source, and may be altered and shared. 

This is a moderated platform. NIST reserves the right to reject, remove, or edit any submission, including anything that: 

* promotes pay-for services or products;  
* includes personally identifiable or business identifiable information according to Department of Commerce Office of Privacy and Open Government [guidelines](http://www.osec.doc.gov/opog/privacy/PII_BII.html); 
* is inaccurate;  
* contains abusive or vulgar content, spam, hate speech, personal attacks, or similar content;
* is clearly "off topic"; 
* makes unsupported accusations; or, 
* contains .exe or .jar file types.* 

*These file types will not be merged into the NIST repository; instead, NIST may link to these if hosted elsewhere. 

## Representations and Warranties & Software Use Agreement 

Any references to commercial entities, products, services, or other nongovernmental organizations or individuals on the site are provided solely for the information of individuals using this page. These references are not intended to reflect the opinion of NIST, the Department of Commerce or the United States, or its officers or employees. Such references are not an official or personal endorsement of any product, person, or service, nor are they intended to imply that the entities, materials, or equipment are necessarily the best available for the purpose. Such references may not be quoted or reproduced for the purpose of stating or implying an endorsement, recommendation, or approval of any product, person, or service. 

This platform is provided as a public service. Information, data, and software posted to this platform is “AS IS.” NIST MAKES NO WARRANTY OF ANY KIND, EXPRESS, IMPLIED OR STATUTORY, INCLUDING, WITHOUT LIMITATION, THE IMPLIED WARRANTY OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, NON-INFRINGEMENT AND DATA ACCURACY. NIST does not warrant or make any representations regarding the use of the software or the results thereof, including but not limited to the correctness, accuracy, reliability or usefulness of the software. You are solely responsible for determining the appropriateness of using and distributing the software and you assume all risks associated with its use, including but not limited to the risks and costs of program errors, compliance with applicable laws, damage to or loss of data, programs or equipment, and the unavailability or interruption of operation. This software is not intended to be used in any situation where a failure could cause risk of injury or damage to property. NIST SHALL NOT BE LIABLE AND YOU HEREBY RELEASE NIST FROM LIABILITY FOR ANY INDIRECT, CONSEQUENTIAL, SPECIAL, OR INCIDENTAL DAMAGES (INCLUDING DAMAGES FOR LOSS OF BUSINESS PROFITS, BUSINESS INTERRUPTION, LOSS OF BUSINESS INFORMATION, AND THE LIKE), WHETHER ARISING IN TORT, CONTRACT, OR OTHERWISE, ARISING FROM OR RELATING TO THE SOFTWARE (OR THE USE OF OR INABILITY TO USE THIS SOFTWARE), EVEN IF NIST HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES.

## Moderators 

### Disassociability Moderators

![Joseph Near](https://github.com/usnistgov/PrivacyEngCollabSpace/blob/master/assets/joseph-near.jpg)

**Joseph Near [@jnear]:** Joseph Near is an assistant professor of computer science at the University of Vermont. His research interests include data privacy, computer security, and programming languages. Joseph received his B.S. in computer science from Indiana University, and his M.S. and Ph.D. in computer science from MIT.

![David Darais](https://github.com/usnistgov/PrivacyEngCollabSpace/blob/master/assets/david-darais.jpg)

**David Darais [@davdar]:** David Darais is a Principal Scientist at Galois, Inc. and supports NIST as a moderator for the Privacy Engineering Collaboration Space. David's research focuses on tools for achieving reliable software in critical, security-sensitive, and privacy-sensitive systems. David received his B.S. from the University of Utah, M.S. from Harvard University and Ph.D. from the University of Maryland.

### Privacy Risk Management Moderator

![Nakia Grayson](https://github.com/usnistgov/PrivacyEngCollabSpace/blob/master/assets/nakia-grayson.jpeg)

**Nakia Grayson [@ngrayson1]:** Nakia Grayson is an IT Security Specialist with the Privacy Engineering Program at the National Institute of Standards and Technology (NIST). She supports the Privacy Engineering Program with development of privacy risk management best practices, guidance and communications efforts. She also leads Supply Chain Assurance project efforts at the National Cybersecurity Center of Excellence (NCCoE). Nakia serves as the Contracting Officer Representative for NIST cybersecurity contracts. She holds a Bachelor’s in Criminal Justice from University of Maryland-Eastern Shore and a Master’s in Information Technology, Information Assurance and Business Administration from the University of Maryland University College.

![Meghan Anderson](https://github.com/usnistgov/PrivacyEngCollabSpace/blob/master/assets/meghan-anderson.jpeg)

**Meghan Anderson [@manderson11]:** Meghan Anderson is a Privacy Risk Strategist with the Privacy Engineering Program at the National Institute of Standards and Technology, U.S. Department of Commerce. She supports the development of privacy engineering, international privacy standards, and privacy risk management guidance. Meghan has a Bachelor’s in Emergency Preparedness, Homeland Security, and Cybersecurity with a concentration in Cybersecurity and a minor in Economics from the University of Albany, SUNY and a Master’s in Cybersecurity from the Georgia Institute of Technology (Georgia Tech).

## NIST Privacy Engineering Program
Learn about NIST's Privacy Engineering Program by visiting our [website](https://www.nist.gov/itl/applied-cybersecurity/privacy-engineering).

## Contact 

Contact NIST to submit feedback, including future topics of interest, or for assistance with contributing to the space: [collabspace@nist.gov](mailto:collabspace@nist.gov)
