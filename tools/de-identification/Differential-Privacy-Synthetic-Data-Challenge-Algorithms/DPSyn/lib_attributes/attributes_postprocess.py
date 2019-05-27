import logging
import json
from itertools import chain

import numpy as np

import config
from lib_view.non_negativity import NonNegativity


class PostprocessAttribute:
    def __init__(self, num_categories, common_parameters):
        self.logger = logging.getLogger("postprocess_attribute")
        
        self.num_categories = num_categories
        self.specs_path = common_parameters["specs_path"]

        self.attributes_group = common_parameters["attributes_group"]
        self.views_group = common_parameters["views_group"]

        self.ordinal_views_dict = common_parameters["ordinal_views_dict"]
        self.ordinal_bin_dict = common_parameters["ordinal_bin_dict"]

        self.recode_significant_indices_dict = common_parameters["recode_significant_indices_dict"]
        self.recode_group_indices_dict = common_parameters["recode_group_indices_dict"]
        self.recode_views_dict = common_parameters["recode_views_dict"]
        
        self.attri_name_index_mapping = common_parameters["attri_name_index_mapping"]
        self.code_mapping = common_parameters["code_mapping"]
        self.onebyone_mapping = common_parameters["onebyone_mapping"]

    #################################### general functions ###################################
    def decode_anchor_attributes(self, records, group_name_list):
        self.logger.info("decoding anchor attributes")
    
        for group_name in group_name_list:
            for attributes_group_key in chain(self.attributes_group.recode_group_key[group_name].keys(),
                                              self.attributes_group.recode_single_key[group_name]):
                
                if attributes_group_key not in self.recode_views_dict:
                    self.logger.warning("attributes group %s has been removed" % (attributes_group_key,))
                else:
                    recode_view = self.recode_views_dict[attributes_group_key]
                    significant_cell_indices = self.recode_significant_indices_dict[attributes_group_key]
                    group_cell_indices = self.recode_group_indices_dict[attributes_group_key]
                    
                    attributes_group_index = self.attributes_group.recode_group_index[attributes_group_key]
                    num_value = self.num_categories[attributes_group_index[0]]
                    record = np.zeros([records.shape[0], len(attributes_group_index)], dtype=np.uint32)
                
                    if group_cell_indices.size == 0:
                        # decode the significant value
                        for anchor_value in range(num_value):
                            anchor_value_indices = np.where(records[:, attributes_group_index[0]] == anchor_value)[0]
            
                            for attri_index, attri in enumerate(attributes_group_index):
                                record[anchor_value_indices, attri_index] = \
                                    recode_view.tuple_key[significant_cell_indices[anchor_value]][attri_index]
                    else:
                        # decode the significant value
                        for anchor_value in range(num_value - 1):
                            anchor_value_indices = np.where(records[:, attributes_group_index[0]] == anchor_value)[0]
                        
                            for attri_index, attri in enumerate(attributes_group_index):
                                record[anchor_value_indices, attri_index] = \
                                    recode_view.tuple_key[significant_cell_indices[anchor_value]][attri_index]
                        
                        # decode the grouped value
                        anchor_value_indices = np.where(records[:, attributes_group_index[0]] == num_value - 1)[0]
                        
                        if anchor_value_indices.size != 0:
                            group_value_dist = recode_view.count[group_cell_indices] / np.sum(recode_view.count[group_cell_indices])
                            group_value_cumsum = np.cumsum(group_value_dist)
                            start = 0
                
                            for index, value in enumerate(group_value_cumsum):
                                end = int(round(value * anchor_value_indices.size))
                    
                                for attri_index, attri in enumerate(attributes_group_index):
                                    record[anchor_value_indices[start: end], attri_index] = \
                                        recode_view.tuple_key[group_cell_indices[index]][attri_index]
                                    
                                start = end
                
                    records[:, attributes_group_index] = record

    def decode_ordinal_attributes(self, records, attribute_dist=None, attribute_bin=None, attribute_index=None):
        def decode(attribute_dist, attribute_bin, attribute_index):
            record = np.copy(records[:, attribute_index])
    
            for value in range(1, attribute_bin.size + 1):
                indices = np.where(record == value)[0]
        
                if value < attribute_bin.size:
                    attri_dist = attribute_dist[attribute_bin[value - 1]: attribute_bin[value]]
                    attri_value = np.arange(attribute_bin[value - 1], attribute_bin[value])
                else:
                    attri_dist = attribute_dist[attribute_bin[value - 1]:]
                    attri_value = np.arange(attribute_bin[value - 1], attribute_dist.size)
        
                if np.sum(attri_dist) != 0:
                    attri_dist /= np.sum(attri_dist)
                    attri_dist_cumsum = np.cumsum(attri_dist)
                    start = 0
            
                    for index, dist in enumerate(attri_dist_cumsum):
                        end = int(round(dist * indices.size))
                
                        records[indices[start: end], attribute_index] = attri_value[index]
                
                        start = end
        
        if attribute_dist is not None:
            self.logger.info("decoding ordinal attribute %s" % (attribute_index,))
            
            decode(attribute_dist, attribute_bin, attribute_index)
            
            np.random.shuffle(records)

        else:
            self.logger.info("decoding ordinal attributes")
            
            records[:, self.attri_name_index_mapping["WKSWORK1"]] = records[:, self.attri_name_index_mapping["WKSWORK2"]] + 1
            records[:, self.attri_name_index_mapping["HRSWORK1"]] = records[:, self.attri_name_index_mapping["HRSWORK2"]] + 1
    
            for attribute_name in self.ordinal_views_dict:
                attribute_dist = self.ordinal_views_dict[attribute_name].normalize_count
                attribute_bin = self.ordinal_bin_dict[attribute_name]
                attribute_index = self.attri_name_index_mapping[attribute_name]
        
                decode(attribute_dist, attribute_bin, attribute_index)
                
                np.random.shuffle(records)
                
    def decode_geo_attributes(self, records, geo_attributes_mapping):
        self.logger.info("decoding geo attributes")
        
        for attribute_name, mapping in geo_attributes_mapping.items():
            attribute_index = self.attri_name_index_mapping[attribute_name]
            record = np.copy(records[:, attribute_index])
            unique_value = np.unique(record)
            
            for value in unique_value:
                indices = np.where(record == value)
                records[indices, attribute_index] = mapping[value]

    def load_mapping_data(self):
        self.general_detail_mapping = json.load(open(config.MAPPING_PATH + "general_detail_mapping.json"))
        self.pair_mapping = json.load(open(config.MAPPING_PATH + "pair_mapping.json"))
    
    def fill_general_from_detail(self, records):
        self.logger.info("filling general from detail")
        
        for general_name in self.general_detail_mapping:
            if general_name in ["BPL", "FBPL", "MBPL"]:
                continue
                
            detail_name = general_name + "D"
            detail_index = self.attri_name_index_mapping[detail_name]
            general_index = self.attri_name_index_mapping[general_name]
            
            record = np.copy(records[:, detail_index])
            unique_value = np.unique(record)
            
            for value in unique_value:
                indices = np.where(record == value)[0]
                detail_code = str(self.code_mapping[detail_name][value])
                general_code = self.general_detail_mapping[general_name][detail_code]
                
                if general_code in self.code_mapping[general_name]:
                    general_value = np.where(self.code_mapping[general_name] == general_code)[0][0]
                    records[indices, general_index] = general_value
                else:
                    self.logger.info("general code do not exist for detail code %s of %s attribute" % (detail_code, detail_name))
                    # todo: determine how to fill value in this situation
                    records[indices, general_index] = 0

        np.random.shuffle(records)

    def fill_pair_mapping_attributes(self, records):
        self.logger.info("filling pairwise mapping")
        
        for anchor_attribute, fill_attributes in self.pair_mapping.items():
            for fill_attribute, mapping in fill_attributes.items():
                anchor_index = self.attri_name_index_mapping[anchor_attribute]
                fill_index = self.attri_name_index_mapping[fill_attribute]
                
                record = np.copy(records[:, anchor_index])
                unique_value = np.unique(record)
            
                for value in unique_value:
                    indices = np.where(record == value)[0]
                    anchor_code = self.code_mapping[anchor_attribute][value]
                    
                    if str(anchor_code) in mapping:
                        fill_code = mapping[str(anchor_code)]
                        
                        if fill_attribute in self.code_mapping:
                            fill_value = np.where(self.code_mapping[fill_attribute] == fill_code)[0][0]
                        else:
                            fill_value = fill_code
                            
                        records[indices, fill_index] = fill_value
                    else:
                        self.logger.info("mapping do not exist for %s for %s and %s" % (anchor_code, anchor_attribute, fill_attribute))
                        # todo: determine how to fill value in this situation
                        records[indices, fill_index] = 0
    
        np.random.shuffle(records)
    
    def fill_onebyone_mapping_attributes(self, records):
        self.logger.info("filling one by one mapping")
        
        for attributes in self.onebyone_mapping:
            anchor_attribute = attributes[0]
            fill_attribute = attributes[1]
            anchor_index = self.attri_name_index_mapping[anchor_attribute]
            fill_index = self.attri_name_index_mapping[fill_attribute]
            
            record = np.copy(records[:, anchor_index])
            unique_value = np.unique(record)
        
            for value in unique_value:
                indices = np.where(record == value)[0]
                fill_value = self.onebyone_mapping[attributes][value]
            
                records[indices, fill_index] = fill_value
    
        np.random.shuffle(records)
        
    ####################################### handling incwage ######################################
    def decode_incwage_C5(self, records, incwage_singleton, incwage_bin):
        self.logger.info("decoding incawge")
        
        incwage_dist = incwage_singleton.normalize_count
        incwage_index = self.attri_name_index_mapping["INCWAGE"]
        record = np.copy(records[:, incwage_index])
    
        for value in range(1, self.num_categories[incwage_index]):
            indices = np.where(record == value)[0]
        
            if value < incwage_bin.size:
                attri_dist = incwage_dist[incwage_bin[value - 1]: incwage_bin[value]]
                attri_value = np.arange(incwage_bin[value - 1], incwage_bin[value])
            else:
                attri_dist = incwage_dist[incwage_bin[value - 1]:]
                attri_value = np.arange(incwage_bin[value - 1], incwage_dist.size)
        
            if np.sum(attri_dist) != 0:
                attri_dist /= np.sum(attri_dist)
                attri_dist_cumsum = np.cumsum(attri_dist)
                start = 0
            
                for index, dist in enumerate(attri_dist_cumsum):
                    end = int(round(dist * indices.size))
                
                    records[indices[start: end], incwage_index] = attri_value[index]
                
                    start = end
                    
        np.random.shuffle(records)

    ############################################### dealing with special attributes ##############################
    def fill_bpl_attributes(self, records):
        self.logger.info("filling bpl attributes")
    
        for attribute_name in ["BPL", "FBPL", "MBPL"]:
            general_name = attribute_name
            detail_name = attribute_name + "D"
        
            record = records[:, self.attri_name_index_mapping[general_name]]
            unique_value = np.unique(record)
        
            for value in unique_value:
                indices = np.where(record == value)[0]
                detail_code = self.code_mapping[general_name][value] * 100
            
                records[indices, self.attri_name_index_mapping[detail_name]] = \
                np.where(self.code_mapping[detail_name] == detail_code)[0][0]
    
        np.random.shuffle(records)

    def fill_geo_attributes(self, records):
        self.logger.info("filling geo attributes")
    
        # fill URBPOP and SIZEPL from CITYPOP
        record = np.copy(records[:, self.attri_name_index_mapping["CITYPOP"]])
        unique_value = np.unique(record)
    
        urbpop_index = self.attri_name_index_mapping["URBPOP"]
        sizepl_index = self.attri_name_index_mapping["SIZEPL"]
    
        for value in unique_value:
            indices = np.where(record == value)[0]
        
            # fill URBPOP
            if ("CITYPOP", "URBPOP") in self.views_group["AGE2"]:
                if value == 0:
                    matrix_count = self.views_group["AGE2"][("CITYPOP", "URBPOP")].calculate_count_matrix()
                    citypop_zero_count = matrix_count[0]
                    non_negativity = NonNegativity(citypop_zero_count)
                    citypop_zero_count = non_negativity.norm_cut()
                    
                    if np.sum(citypop_zero_count) == 0:
                        records[indices, urbpop_index] = 0
                    else:
                        zero_count_cumsum = np.cumsum(citypop_zero_count) / np.sum(citypop_zero_count)
                        start = 0
                        
                        for index, dist in enumerate(zero_count_cumsum):
                            end = int(round(dist * indices.size))
                            records[indices[start: end], urbpop_index] = index
                            start = end
                    
                elif value > 0 and value < 25:
                    records[indices, urbpop_index] = 0
                else:
                    records[indices, urbpop_index] = value
        
            # fill SIZEPL, RHS is the encoded value, not actual value for SIZEPL
            if value < 10:
                records[indices, sizepl_index] = 1
            elif value >= 10 and value < 25:
                records[indices, sizepl_index] = 2
            elif value >= 25 and value < 40:
                records[indices, sizepl_index] = 3
            elif value >= 40 and value < 50:
                records[indices, sizepl_index] = 4
            elif value >= 50 and value < 100:
                records[indices, sizepl_index] = 5
            elif value >= 100 and value < 250:
                records[indices, sizepl_index] = 6
            elif value >= 250 and value < 500:
                records[indices, sizepl_index] = 7
            elif value >= 500 and value < 750:
                records[indices, sizepl_index] = 8
            elif value >= 750 and value < 1000:
                records[indices, sizepl_index] = 9
            elif value >= 1000 and value < 2000:
                records[indices, sizepl_index] = 10
            elif value >= 2000 and value < 3000:
                records[indices, sizepl_index] = 11
            elif value >= 3000 and value < 4000:
                records[indices, sizepl_index] = 12
            elif value >= 4000 and value < 5000:
                records[indices, sizepl_index] = 13
            elif value >= 5000 and value < 6000:
                records[indices, sizepl_index] = 14
            elif value >= 6000 and value < 7500:
                records[indices, sizepl_index] = 15
            elif value >= 7500 and value < 10000:
                records[indices, sizepl_index] = 16
            elif value >= 10000 and value < 20000:
                records[indices, sizepl_index] = 17
            else:
                records[indices, sizepl_index] = 18
    
        np.random.shuffle(records)
        
    def fill_supdist_attribute(self, records, sigma):
        self.logger.info("filling supdist attribute")
        
        county_supdist_matrix_count = self.views_group["AGE2"][("COUNTY", "SUPDIST")].calculate_count_matrix()
        county_supdist_matrix_count = np.transpose(county_supdist_matrix_count)
        
        county_index = self.attri_name_index_mapping["COUNTY"]
        supdist_index = self.attri_name_index_mapping["SUPDIST"]
        record = np.copy(records[:, county_index])
        unique_value = np.unique(record)
        
        for value in unique_value:
            indices = np.where(record == value)[0]
            valid_supdist_index = np.where(county_supdist_matrix_count[value] >= 4.5 * sigma)[0]
            
            if valid_supdist_index.size == 0:
                valid_supdist_index = np.argmax(county_supdist_matrix_count[value])
                records[indices, supdist_index] = valid_supdist_index
            elif valid_supdist_index.size == 1:
                records[indices, supdist_index] = valid_supdist_index
            else:
                valid_count = county_supdist_matrix_count[value, valid_supdist_index]
                valid_count_cumsum = np.cumsum(valid_count) / np.sum(valid_count)
                start = 0
                
                for index, dist in enumerate(valid_count_cumsum):
                    end = int(round(dist * indices.size))
                    records[indices[start: end], supdist_index] = valid_supdist_index[index]
                    start = end
            
        np.random.shuffle(records)
    
    def fill_citizen_attribute(self, records):
        self.logger.info("filling citizen attribute")
        
        bpl_index = self.attri_name_index_mapping["BPL"]
        citizen_index = self.attri_name_index_mapping["CITIZEN"]
        threshold_index = np.where(self.code_mapping["BPL"] == 99)[0]
    
        # when BPL <= 99, set CITIZEN = 0
        under_indices = np.where(records[:, bpl_index] <= threshold_index)[0]
        records[under_indices, citizen_index] = 0
    
        # when BPL > 99, fill CITIZEN based on its distribution
        over_indices = np.where(records[:, bpl_index] > threshold_index)[0]
        citizen_dist = self.views_group["AGE1"][("CITIZEN",)].normalize_count[1:]
        
        if np.sum(citizen_dist) != 0:
            citizen_cumsum = np.cumsum(citizen_dist) / np.sum(citizen_dist)
            start = 0
        
            for index, dist in enumerate(citizen_cumsum):
                end = int(round(dist * over_indices.size))
            
                records[over_indices[start: end], citizen_index] = index + 1
            
                start = end
    
        np.random.shuffle(records)
        
    

