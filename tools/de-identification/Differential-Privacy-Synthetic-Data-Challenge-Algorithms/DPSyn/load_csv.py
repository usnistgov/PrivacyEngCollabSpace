import logging
import pickle
import csv
import json

import numpy as np

import config


class LoadCSV:
    def __init__(self):
        self.logger = logging.getLogger("load_csv")
        self.attri_name_index_mapping = {}

    def load_original_records(self, dataset_path):
        self.logger.info("loading raw data")
        
        self.encoded_records = np.genfromtxt(dataset_path, delimiter=",", skip_header=1, filling_values=0.0)

        if len(self.encoded_records.shape) == 1:
            self.encoded_records = self.encoded_records.reshape((1, self.encoded_records.size))
        
        self.logger.info("loaded %s records" % (self.encoded_records.shape[0]))
    
    def load_dataset_parameters(self, dataset_path, json_path):
        self.logger.info("loading data parameters")

        # read dataset header and spec file
        dataset = csv.reader(open(dataset_path, newline=''), dialect='excel')
        self.dataset_header = next(dataset)
        self.dataset_spec = json.load(open(json_path))
        
        for index, attribute_name in enumerate(self.dataset_header):
            self.attri_name_index_mapping[attribute_name] = index
        
        # read code mapping
        self.code_mapping = pickle.load(open(config.MAPPING_PATH + "code_mapping", "rb"))
        
        self.logger.info("loaded data parameters")
        
    def calculate_num_categories(self):
        self.logger.info("calculating num_categories")
        
        self.num_categories = np.zeros(self.encoded_records.shape[1], dtype=np.int64)
        
        for index, attribute_name in enumerate(self.dataset_header):
            maxval = self.dataset_spec[attribute_name]["maxval"]
            
            if attribute_name in self.code_mapping:
                maxval_index = np.where(self.code_mapping[attribute_name] == maxval)[0]
                
                if maxval_index.size == 0:
                    self.num_categories[index] = maxval + 1
                    self.code_mapping[attribute_name] = np.arange(maxval + 1, dtype=np.uint32)
                else:
                    self.num_categories[index] = maxval_index[0] + 1
            else:
                self.num_categories[index] = maxval + 1

        self.logger.info("calculated num_categories")

    def transform_records_to_num(self):
        self.logger.info("transforming the records")
        
        self.records = np.zeros([self.encoded_records.shape[0], self.encoded_records.shape[1]], dtype=np.uint32)
        
        for index, attribute_name in enumerate(self.dataset_header):
            self.logger.info("transforming attribute %s: %s" % (attribute_name, index))
            
            # if attribute_name in self.code_mapping and attribute_name not in self.inconsistent_attributes:
            if attribute_name in self.code_mapping:
                records = self.encoded_records[:, index]
                unique_value, count = np.unique(records, return_counts=True)
                
                for value in unique_value:
                    code_mapping_index = np.where(self.code_mapping[attribute_name] == value)[0]
                    self.records[records == value, index] = code_mapping_index
            else:
                self.records[:, index] = self.encoded_records[:, index]
                
        self.logger.info("transformed the records")
    
    