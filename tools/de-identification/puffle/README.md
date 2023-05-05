# puffle

**Primary Focus Area (select one):** De-identification

**De-identification Keywords (select any relevant):** Differential Privacy, Machine Learning, Federated Learning, Model Personalization

**Brief Description:**
This tool contains the solution of team puffle at the [US/UK PETs Prize Challenge](https://www.drivendata.org/competitions/group/nist-federated-learning/) that won [1st place](https://drivendata.co/blog/federated-learning-pets-prize-winners-phases-2-3) in the Pandemic Forecasting Track. Our solution is a simple, general, and easy-to-use multi-task learning (MTL) framework that balances the interplay between privacy, utility, and data heterogeneity in private cross-silo federated learning. Our framework involves three key components: (1) model personalization for capturing data heterogeneity across data silos, (2) local noisy gradient descent for silo-specific, node-level differential privacy in contact graphs, and (3) model mean-regularization to balance privacy-heterogeneity trade-offs and minimize the loss of accuracy. Combined together, our framework can provide differential privacy with flexible data granularity and improved privacy-utility tradeoffs; has high adaptability to gradient-based learning algorithms; and is simple to implement and tune. Our solution is in part based on our NeurIPS'22 [paper](https://arxiv.org/abs/2206.07902) studying privacy and personalization in cross-silo federated learning.


**GitHub User Serving as POC (or Email Address):** @kenziyuliu

**Affiliation/Organization(s) Contributing (if relevant):** Carnegie Mellon University, School of Computer Science

**Tool Link:** https://github.com/kenziyuliu/pets-challenge
