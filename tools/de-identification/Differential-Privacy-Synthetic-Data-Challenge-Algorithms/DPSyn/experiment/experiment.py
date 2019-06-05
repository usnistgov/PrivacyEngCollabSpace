import logging

import numpy as np

from load_csv import LoadCSV
from generate_submission import GenerateSubmission


class Experiment:
    def __init__(self, path, anonymization):
        self.logger = logging.getLogger("experiment")

        self.input_path = path["input_path"]
        self.output_path = path["output_path"]
        self.specs_path = path["specs_path"]
        
        self.epsilon = anonymization["epsilon"]
        self.delta = anonymization["delta"]
        self.sensitivity = anonymization["sensitivity"]
        
        self.load_dataset()

        self.num_records = self.records.shape[0]
        self.num_attributes = self.num_categories.size
        self.header_mapping = self.generate_header_mapping()

    def load_dataset(self):
        self.logger.info("loading original dataset")
    
        csv = LoadCSV()
        csv.load_original_records(self.input_path)
        csv.load_dataset_parameters(self.input_path, self.specs_path)
        csv.calculate_num_categories()
        csv.transform_records_to_num()

        self.records = csv.records
        self.num_categories = csv.num_categories
        self.dataset_header = csv.dataset_header
        self.attri_name_index_mapping = csv.attri_name_index_mapping
        self.code_mapping = csv.code_mapping
    
        self.original_num_categories = np.copy(self.num_categories)
        self.original_records = np.copy(self.records)
    
        self.logger.info("loaded original dataset")

    def generate_submission_dataset(self, records):
        submission = GenerateSubmission(self.attri_name_index_mapping)
        submission.load_records(records)
        submission.generate_csv(self.dataset_header, self.code_mapping, self.output_path)
            
    def generate_header_mapping(self):
        header_mapping = {}
        
        for index, name in enumerate(self.dataset_header):
            header_mapping[name] = index
            
        return header_mapping
