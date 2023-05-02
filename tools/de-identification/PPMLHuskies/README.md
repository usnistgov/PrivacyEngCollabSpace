# PPMLHuskies

**Primary Focus Area (select one):** De-identification

**De-identification Keywords (select any relevant):** Differential Privacy, Homomorphic Encryption, Machine Learning, Federated Learning, 

**Brief Description:**
We propose a cross-silo federated architecture in which a payment network system (PNS) denoted by $\mathcal{S}$ has labeled data to train a model $\mathcal{M}$ for detection of anomalous payments. The other entities in the federation are banks $\mathcal{B}_1, \mathcal{B}_2, \ldots, \mathcal{B}_n$ that collaborate with $\mathcal{S}$ to create feature values to improve the utility of $\mathcal{M}$. To jointly extract feature values in a privacy-preserving manner, $\mathcal{S}$ and the banks engage in cryptographic protocols to perform computations over their joint data, without the need for $\mathcal{S}$ and the banks to disclose their data in an unencrypted manner to each other, i.e. our solution provides _input privacy_ through encryption, with mathematically verifiable guarantees. To the best of our knowledge, such joint privacy-preserving feature extraction in a federation with horizontally and vertically partitioned data is novel.

Furthermore, to prevent the model from memorizing instances from the training data, the model is trained with a machine learning (ML) algorithm that provides Differential Privacy (DP). Our overall solution therefore provides both _input privacy_, as none of the entities in the federation ever sees the data of any of the other entities in an unencrypted manner, and _output privacy_, as the model and any inferences with that model avoid information leakage about the underlying training data under DP guarantees.

For the privacy-preserving feature extraction we propose a custom protocol based on elliptic curve-based ElGamal and oblivious key-value stores (OKVS). The model is a neural network trained with DP-SGD. We prove that our overall solution is secure in the honest-but-curious setting. Experimental results demonstrate that our solution is efficient and scalable, and that it yields accurate models while preserving input and output privacy.


**GitHub User Serving as POC (or Email Address):** golobs@uw.edu

**Affiliation/Organization(s) Contributing (if relevant):** University of Washington Tacoma, Universidade de Brasilia, TU Delft

**Tool Link:** https://github.com/steveng9/PETsChallenge
