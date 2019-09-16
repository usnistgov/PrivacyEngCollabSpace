import logging
import json

import numpy as np


class PreprocessAttribute:
    def __init__(self, records, num_categories, common_parameters):
        self.logger = logging.getLogger("preprocess_attribute")
        
        self.records = records
        self.num_categories = num_categories
        
        self.code_mapping = common_parameters["code_mapping"]
        self.specs_path = common_parameters["specs_path"]
        self.attri_name_index_mapping = common_parameters["attri_name_index_mapping"]
        self.incwage_bin_value = common_parameters["incwage_bin_value"]

    def refine_geo_attributes(self):
        self.logger.info("refining geo attribute")
        geo_attributes_mapping = {}
        
        for attribute_name in ["COUNTY", "METAREAD", "CITY"]:
            attribute_index = self.attri_name_index_mapping[attribute_name]
            record = np.copy(self.records[:, attribute_index])
            unique_value = np.unique(record)
            
            for index, value in enumerate(unique_value):
                indices = np.where(record == value)[0]
                self.records[indices, attribute_index] = index
                
            self.num_categories[attribute_index] = unique_value.size
            geo_attributes_mapping[attribute_name] = unique_value
            
        return geo_attributes_mapping
        
    def bucketize_attribute(self, attribute_name, attribute_bin):
        attribute_index = self.attri_name_index_mapping[attribute_name]
        bucketized_value = np.digitize(self.records[:, attribute_index], attribute_bin)
        self.records[:, attribute_index] = bucketized_value
        self.num_categories[attribute_index] = attribute_bin.size + 1
        
    def bucketize_enumdist(self):
        enumdist_bin = [100 * x for x in range(31)]
        
        enumdist_bin = np.array(enumdist_bin)
        
        self.bucketize_attribute("ENUMDIST", enumdist_bin)
        
        return enumdist_bin
        
    def bucketize_rent(self):
        rent_bin = [0]
        rent_bin += [1 + 5 * x for x in range(6)]
        rent_bin += [31 + 10 * x for x in range(2)]
        rent_bin += [51, 101, 9998]
    
        rent_bin = np.array(rent_bin)
    
        self.bucketize_attribute("RENT", rent_bin)
    
        return rent_bin
    
    def bucketize_valueh(self):
        valueh_bin = [0]
        valueh_bin += [500 + 500 * x for x in range(8)]
        valueh_bin += [4999, 6999, 9999, 10000, 9999998, 9999999]
    
        valueh_bin = np.array(valueh_bin)
    
        self.bucketize_attribute("VALUEH", valueh_bin)
    
        return valueh_bin
    
    def bucketize_famsize(self):
        famsize_bin = [1 + x for x in range(10)]
    
        famsize_bin = np.array(famsize_bin)
    
        self.bucketize_attribute("FAMSIZE", famsize_bin)
    
        return famsize_bin

    def bucketize_age_1(self):
        age_bin = [10 * x for x in range(7)]
    
        age_bin = np.array(age_bin)
    
        self.bucketize_attribute("AGE", age_bin)
    
        return age_bin
    
    def bucketize_age_2(self):
        age_bin = [x for x in range(31)]
        age_bin += [31 + 2 * x for x in range(4)]
        age_bin += [39 + 3 * x for x in range(7)]
        age_bin += [60 + 5 * x for x in range(3)]
        age_bin += [75, 101]
    
        age_bin = np.array(age_bin)
    
        self.bucketize_attribute("AGE", age_bin)
    
        return age_bin
    
    def bucketize_incwage_4(self):
        incwage_bin = [0, 1]
        incwage_bin += [100 + 100 * x for x in range(10)]
        incwage_bin += [1200, 1500, 1800, 2200, 3000, 999998]
    
        incwage_bin = np.array(incwage_bin)
    
        self.bucketize_attribute("INCWAGE", incwage_bin)
    
        return incwage_bin
    
    def bucketize_incwage_5(self):
        incwage_bin = [0, 1, 200, 500, 800, 1200, 1800, 999998]
    
        incwage_bin = np.array(incwage_bin)
    
        self.bucketize_attribute("INCWAGE", incwage_bin)
    
        return incwage_bin

    def bucketize_incwage_6(self):
        incwage_bin = [0, 1, 400, 900, 1500, 999998]
    
        incwage_bin = np.array(incwage_bin)

        attribute_index = self.attri_name_index_mapping["INCWAGE"]
        original_incwage_record = np.copy(self.records[:, attribute_index])
        
        bucketized_value = np.digitize(self.records[:, attribute_index], incwage_bin)
        self.records[:, attribute_index] = bucketized_value
        self.num_categories[attribute_index] = incwage_bin.size + 1
    
        return incwage_bin, original_incwage_record

    def bucketize_incwage_7(self):
        incwage_bin = [0, 1, 200, 400, 700, 900, 1200, 1500, 2000, 999998]
    
        incwage_bin = np.array(incwage_bin)
    
        self.bucketize_attribute("INCWAGE", incwage_bin)
    
        return incwage_bin
    
        
        
    