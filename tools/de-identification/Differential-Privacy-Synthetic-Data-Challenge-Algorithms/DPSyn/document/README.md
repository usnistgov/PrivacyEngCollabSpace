# Overview
The program starts from main.py and calls "experiment/experiment_C5_1-C5_2.py" for different epsilon input. "experiment/experiment_C5_1-C5_2.py" contains the main procedures to generate the synthetic dataset, they will invoke functions in other modules to implement corresponding tasks. Specifically, "configuration_C5_1-C5_2()" functions is responsible for constructing the noisy marginals, which is the only part that touches the private dataset. The consist_views(), synthesize_records() and post_processing() functions are for post-processing step.

# Run the code
Our code receives 4 positional arguments and 5 optional arguments as listed in the main.py file.  Here is an example:

```
python main.py colorado.csv out.csv colorado-specs.json 1.0
```

Note that the data file colorado.csv and specs file colorado-specs.json are not included in the repository, one can download them from the topcoder platform for the third challenge.

# Functionality of each file
## General code
* main.py: the main file, program starts from here
* experiment/experiment_C5_1-C5_2.py: contains the main procedures to generate the synthetic dataset, they will invoke functions in other modules
* experiment/experiment_C5.py: contains the functions share by experiment_C5_1.py and experiment_C5_2.py
* config.py: define some global constants
* lib_composition/advanced_composition.py: determine privacy budget allocation using Renyi-DP
* lib_view/view.py: some basic methods to process marginals/views
* query.py, scoring.py, utility.py, evaluation/marginal.py, evaluation/range_query.py, evaluation/income_property.py: designed for local evaluation
* experiment/experiment_dpsyn.py: contains functions to construct marginals, and functions for local evaluation.

## Pre-processing code
* load_csv.py: load data from dataset, and pre-process the data into numpy format. Most of the operations in our code are based on numpy operation
* experiment/experiment.py: call the functions in load_csv.py to load dataset
* lib_attributes/attributes_preprocess.py: preprocess the original dataset for the algorithms, such as extract distinct values for attributes CITY and COUNTY.

## Privatization code
* experiment/experiment_C5_1-C5_2.py: "configuration_C5_1-C5_2()" functions in these modules are responsible for constructing the noisy marginals, which is the only part that touches the private dataset. The following module would be invoked if necessary.
* lib_attributes/attributes_recode.py: recode and compress attributes using certain amount of privacy budget.

## Post-processing code
* lib_view/consistent.py: make the noisy marginals consistent
* lib_dpsyn/records_update.py: use the noisy marginals to update a randomly generated synthetic dataset
* lib_attributes/attributes_postprocess: all the functions are designed for post-processing the synthetic dataset
* generate_submission.py: transform the synthetic dataset from numpy format to the original dataset format

# Running time
* When epsilon <= 0.2, the program takes about 40 minutes to generate the synthetic dataset for the Colorado dataset
* When epsilon > 0.2, the program takes about 50 minutes to generate the synthetic dataset for the Colorado dataset











