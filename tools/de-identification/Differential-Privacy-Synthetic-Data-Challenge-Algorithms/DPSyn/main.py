import logging
import argparse

from experiment.experiment_C5_1 import Experiment_C5_1
from experiment.experiment_C5_2 import Experiment_C5_2


def config_logger():
    # create logger
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # create console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(levelname)s:%(asctime)s: - %(name)s - : %(message)s')
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(ch)

    
def main(path, anonymization, synthesizer):
    if anonymization["epsilon"] <= 0.2:
        Experiment_C5_1(path, anonymization, synthesizer)
    elif anonymization["epsilon"] > 0.2:
        Experiment_C5_2(path, anonymization, synthesizer)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    ################################### interface to final scoring ##################################
    parser.add_argument("input_path", type=str)
    parser.add_argument("output_path", type=str)
    parser.add_argument("specs_path", type=str)
    parser.add_argument("epsilon", type=float)

    ####################################### general parameters ###################################
    # specify privacy parameters
    parser.add_argument('--delta', type=float, default=1.0 / (662000 ** 2))
    parser.add_argument('--sensitivity', type=float, default=1.0)

    # parameters for views generation
    parser.add_argument('--consist_iterations', type=int, default=100)
    
    # parameters for dpsyn_mcf method
    parser.add_argument('--synthesizer_num_records', type=int, default=662000)
    parser.add_argument('--update_iterations', type=int, default=100)

    args = parser.parse_args()
    config_logger()

    path = {
        "input_path": args.input_path,
        "output_path": args.output_path,
        "specs_path": args.specs_path,
    }
    anonymization = {
        "epsilon": args.epsilon,
        "delta": args.delta,
        "sensitivity": args.sensitivity
    }
    synthesizer = {
        "num_records": args.synthesizer_num_records,
        "update_iterations": args.update_iterations,
        "consist_iterations": args.consist_iterations,
    }
    
    main(path, anonymization, synthesizer)