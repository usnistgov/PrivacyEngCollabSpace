import csv
import logging

import numpy as np


class GenerateSubmission:
    def __init__(self, attri_name_index_mapping):
        self.logger = logging.getLogger("generate_submission")
        
        self.attri_name_index_mapping = attri_name_index_mapping
    
    def load_records(self, records):
        self.records = records
    
    def generate_csv(self, dataset_header, code_mapping, output_path):
        save_file = open(output_path, 'w', newline='')
        
        save_csv = csv.writer(save_file, dialect='excel')
        
        save_csv.writerow(dataset_header)

        self.logger.info("mapping attributes")
        
        for attribute_name in code_mapping:
            if attribute_name in self.attri_name_index_mapping:
                self.logger.info("mapping %s" % (attribute_name,))
                
                attribute_index = self.attri_name_index_mapping[attribute_name]
                unique_value = np.unique(self.records[:, attribute_index])
                attri_records = np.zeros(self.records.shape[0])
            else:
                continue
            
            for value in unique_value:
                indices = np.where(self.records[:, attribute_index] == value)[0]
                attri_records[indices] = code_mapping[attribute_name][value]
                
            self.records[:, attribute_index] = attri_records

        self.logger.info("writing records")
        
        for i in range(self.records.shape[0]):
            if i % 10000 == 0:
                self.logger.info("processing %s records" % (i,))
            
            record = np.ndarray.tolist(self.records[i])
            
            save_csv.writerow(record)
    