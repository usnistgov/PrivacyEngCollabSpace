# Visa-Pets-FL

Copyright 2023 Visa

This code is meant only as a reference for the Privacy-enhancing technologies (PETs) challenge organized by NIST & NSF on behalf of the U.S. government. The code is specifically written for the competition's test harness. The current implementation would have to be modified to run in a real-world environment. This is not a Visa Product and Visa doesn't guarantee the code is maintained or bug free.

Our solution folder consists of three components, a centralized solution, a federated solution, and the source code for an oblivious transfer shared library, which we use in our federated solution. We describe the files below:

* *DataObjects.py:* Defines the train and test datasets
* *DataPrepUtils.py:* Data pre-processing code 
* *DNNCentralizedModule.py:* The main centralized code logic
* *NeuralNet.py:* Defines the neural network configuration
* *solution_centralized.py:* The exposed APIs for the execution harness. After pre-processing the data, both fit() and predict() call the corresponding functions in the DNNCentralizedModule.py
* *DNN.py:* Helper functions for the training and inference flows, including flattening per-sample gradient updates into 1d tensors, masking gradients, converting gradients to and from integers.
* *libwrapper.so:* The shared library exposes the apis for us to do oblivious transfer, saving symmetric keys to disk and symmetric encryption & decryption process.
* *ot.py:* Loads and exposes the api of the oblivious transfer library.
* *solution_federated.py:* Our federated solution. The solution contains Client and Strategy functions for both the train and test phases:

## Instructions

Traverse into the ot_library & build the library based upon the readme file present inside the folder. The library would be created under ./out/build/<platform>/wrapper/. Copy the dynamic library libwrapper into the federated folder.

See the below repo for instructions on how to use the runtime container to run the solution:
https://github.com/drivendataorg/pets-prize-challenge-runtime/tree/main/runtime