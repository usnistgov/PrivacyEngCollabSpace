# rmckenna - Differential Privacy Synthetic Data Challenge Algorithm

## Team Member and Affiliation: 
Ryan McKenna (ryan112358; UMass Amherst)

## Brief Description
The high-level idea is to (1) use the Gaussian mechanism to obtain noisy answers to a carefully selected set of counting queries (1, 2, and 3 way marginals) and (2) find a synthetic data set that approximates the true data with respect to those queries.  The latter step is accomplished with [3], and the previous step uses ideas inspired by [1] and [2].  More specifically, this is done by calculating the mutual information (on the public dataset) for each pair of attributes and selecting the marginal queries that have high mutual information. 

[1] Zhang, Jun, et al. "Privbayes: Private data release via bayesian networks." ACM Transactions on Database Systems (TODS) 42.4 (2017): 25.

[2] Chen, Rui, et al. "Differentially private high-dimensional data publication via sampling-based inference." Proceedings of the 21th ACM SIGKDD International Conference on Knowledge Discovery and Data Mining. ACM, 2015.

[3] McKenna, Ryan, Daniel Sheldon, and Gerome Miklau. "Graphical-model based estimation and inference for differential privacy." Proceddings of the 36th International Conference on Machine Learning. 2019.

## Setup:
First make sure all the necessary python dependencies are installed.  These are numpy, scipy, pandas, and networkx.  Then clone these repositories and follow the necessary setup instructions: 

[1] https://github.com/ryan112358/private-pgm

[2] https://github.com/tensorflow/privacy


## Running the code:
To generate synthetic data, run the following code:

$ python match3.py --dataset colorado.csv --specs colorado-specs.json --epsilon 1.0 --delta 2.2820544e-12 --save synthetic-1.0.csv

The file assumes the data has the same columns as the provisional dataset (colorado.csv), but the possible values for each column may be different.  As per the match 3 rules, the set of unique values for geographic attributes is directly calculated on the input dataset, although in reality it should be provided externally as public information.  The mechanism may be time consuming, requiring a few hours to complete, depending on the machine it is being run on.
