<h1>Differential Privacy Synthetic Data Challenge Algorithms</h1>

<strong>De-identification Keywords:</strong> Differential Privacy, Synthetic Data Generation

<strong>Brief Description:</strong> Participants in Match #3 of the [2018 Differential Privacy Synthetic Data Challenge](https://www.nist.gov/ctl/pscr/funding-opportunities/prizes-challenges/2018-differential-privacy-synthetic-data-challenge) developed these open source algorithms as part of an effort to advance differential privacy. Participants were challenged to create new methods, or improve existing methods of data de-identification, while preserving the dataset’s utility for analysis. All solutions were required to satisfy the differential privacy guarantee, a provable guarantee of individual privacy protection. Participants used a data set of emergency response events occurring in San Francisco and a sub-sample of the IPUMS USA data for the 1940 U.S. Census.

<em>Contributions are listed in alphabetical order.</em>

<h1>DP_WGAN-UCLANESL</h1>
<strong>Team Members:</strong> Prof. Mani Srivastava (@msrivastava) - Team Captain (Match 1 and Match 3), Moustafa Alzantot (@malzantot) - (Match 1 and Match 3), Nat Snyder (@natsnyder1) - Match 1, Supriyo Charkaborty (@supriyogit) - Match 1

<strong>Brief Description:</strong> This repo contains an implementation for the award-winning solution to the 2018 Differential Privacy Synthetic Data Challenge by team UCLANESL. Our solution has been awarded the 5th place in Match#3 of the challenge and an earlier version has also won the 4th place in Match #1. The solution trains a wasserstein generative adversarial network (w-GAN) that is trained on the real private dataset. Differentially private training is applied by santizing (norm clipping and adding Gaussian noise) the gradients of the discriminator. Once the model is trained, it can be used to generate sytnethic dataset by feeding random noise into the generator.

Link: https://github.com/usnistgov/PrivacyEngCollabSpace/tree/master/tools/de-identification/Differential-Privacy-Synthetic-Data-Challenge-Algorithms/DP_WGAN-UCLANESL
https://github.com/nesl/nist_differential_privacy_synthetic_data_challenge

<h1>DPSyn</h1>
<strong>Team Members & Affiliations:</strong> Ninghui Li (Purdue University), Zhikun Zhang (Zhejiang University), Tianhao Wang (Purdue University)

<strong>Brief Description:</strong> We present DPSyn, an algorithm for synthesizing microdata while satisfying differential privacy, and its instantiation to the dataset used in the competition, namely Public Use Microdata Sample (PUMS) of the 1940 USA Census Data.

Link: https://github.com/usnistgov/PrivacyEngCollabSpace/tree/master/tools/de-identification/Differential-Privacy-Synthetic-Data-Challenge-Algorithms/DPSyn

<h1>rmckenna</h1>
<strong>Team Member & Affiliation:</strong> Ryan McKenna (UMass Amherst)

<strong>Brief Description:</strong> the first place entry in the third round of the NIST Differential Privacy Synthetic Data Challenge
The high-level idea is to (1) use the Gaussian mechanism to obtain noisy answers to a carefully selected set of counting queries (1, 2, and 3 way marginals) and (2) find a synthetic data set that approximates the true data with respect to those queries. The latter step is accomplished with [3], and the previous step uses ideas inspired by [1] and [2]. More specifically, this is done by calculating the mutual information (on the public dataset) for each pair of attributes and selecting the marginal queries that have high mutual information.

[1] Zhang, Jun, et al. "Privbayes: Private data release via bayesian networks." ACM Transactions on Database Systems (TODS) 42.4 (2017): 25.
[2] Chen, Rui, et al. "Differentially private high-dimensional data publication via sampling-based inference." Proceedings of the 21th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. ACM, 2015.
[3] McKenna, Ryan, Daniel Sheldon, and Gerome Miklau. "Graphical-model based estimation and inference for differential privacy." Proceddings of the 36th International Conference on Machine Learning. 2019.

Link: https://github.com/usnistgov/PrivacyEngCollabSpace/tree/master/tools/de-identification/Differential-Privacy-Synthetic-Data-Challenge-Algorithms/rmckenna
