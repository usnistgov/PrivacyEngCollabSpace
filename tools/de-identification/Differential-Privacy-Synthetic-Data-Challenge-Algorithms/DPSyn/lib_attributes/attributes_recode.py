import logging
import math

import numpy as np

from lib_view.view import View


class RecodeAttribute:
    def __init__(self, records, num_categories, common_parameters):
        self.logger = logging.getLogger("recode_attribute")
        
        self.records = records
        self.num_categories = num_categories
        
        self.attributes_group_views_dict = {}

        self.epsilon = common_parameters["epsilon"]
        self.num_records_estimation = common_parameters["num_records_estimation"]
        self.attributes_group = common_parameters["attributes_group"]
        
        self.recode_significant_indices_dict = common_parameters["recode_significant_indices_dict"]
        self.recode_group_indices_dict = common_parameters["recode_group_indices_dict"]
        self.recode_views_dict = common_parameters["recode_views_dict"]
        
        self.views_group = common_parameters["views_group"]
        self.views_iterate_key = common_parameters["views_iterate_key"]
        self.views_consist_key = common_parameters["views_consist_key"]
        # self.views_iterate_key_B = common_parameters["views_iterate_key_B"]

    def attributes_group_anonymize(self, attributes_group_key, sensitivity, gauss_sigma, recode_times=0, epsilon=0.0, is_anonymize=True):
        attributes_group = self.attributes_group.recode_group_index[attributes_group_key]
        indicator = np.zeros(len(self.num_categories), dtype=np.uint8)
        indicator[attributes_group] = 1
    
        # choose the cells with values above threshold
        view = View(indicator, self.num_categories)
        view.calculate_tuple_key()
        view.count_records(self.records)
    
        if is_anonymize or self.epsilon == -1.0:
            if epsilon != 0.0:
                view.count += np.random.laplace(scale=sensitivity / epsilon, size=view.num_key)
            else:
                view.count += np.random.normal(scale=gauss_sigma, size=view.num_key)
    
        self.attributes_group_views_dict[attributes_group_key] = view
        
        if recode_times == 0:
            self.num_records_estimation[0] += np.sum(view.count)

    def attributes_recode(self, attributes_group_key, threshold, recode_times=0):
        self.logger.info("recoding group %s" % (attributes_group_key,))

        special_attribute = ["CITY", "METAREAD"]
    
        # load view generate from attributes_group_anonymize function
        attributes_group_index = self.attributes_group.recode_group_index[attributes_group_key]
        view = self.attributes_group_views_dict[attributes_group_key]
        
        if attributes_group_key not in special_attribute:
            view.non_negativity("N1")
    
        # find the significant value
        significant_cell_indices = np.where(view.count >= threshold)[0]
        group_cell_indices = np.where(np.logical_and(view.count < threshold, view.count > 0))[0]
        
        # keep the top-k values
        num_keep_value = 14 + int(math.floor(self.epsilon * 5))
        
        if significant_cell_indices.size > num_keep_value:
            # if attributes_group_key not in ["CITYPOP"]:
            sort_index = np.argsort(view.count)
            keep_indices = sort_index[-num_keep_value:]
            group_cell_indices = np.union1d(group_cell_indices, np.setdiff1d(significant_cell_indices, keep_indices))
            significant_cell_indices = keep_indices
        
        # encode the cells with values above threshold
        encode_records = np.matmul(self.records[:, attributes_group_index], view.encode_num)
        new_record = np.zeros(self.records.shape[0], dtype=np.uint32)
        significant_records_indices = np.zeros(0)
    
        for index, value in enumerate(significant_cell_indices):
            indices = np.where(encode_records == value)[0]
            new_record[indices] = index
            significant_records_indices = np.union1d(significant_records_indices, indices)
    
        # encode the cells with values below threshold
        remain_indices = np.setdiff1d(np.arange(self.records.shape[0]), significant_records_indices)
        num_group = np.sum(view.count[group_cell_indices])
        significant_value = view.count[significant_cell_indices]
        significant_ratio = significant_value / np.sum(significant_value)
        significant_ratio_cumsum = np.cumsum(significant_ratio)
        group_value_threshold = 0
        
        # remain the grouped value if their number exceed some threshold
        if num_group > group_value_threshold and attributes_group_key not in special_attribute:
            new_record[remain_indices] = significant_cell_indices.size
        else:
            group_cell_indices = np.zeros(0)
            significant_value += significant_ratio * remain_indices.size
            
            start = 0
    
            for index, ratio in enumerate(significant_ratio_cumsum):
                end = int(round(len(remain_indices) * ratio))
                new_record[remain_indices[start: end]] = index
                start = end
    
        ################################# update global parameters #####################################
        if num_group > group_value_threshold and attributes_group_key not in special_attribute:
            num_categories = significant_cell_indices.size + 1
        else:
            num_categories = significant_cell_indices.size
        
        if num_categories == 0:
            self.num_categories[attributes_group_index[0]] = num_categories

            self.logger.info("maximum remain: %s, actual remain: %s" % (num_keep_value, num_categories))
        else:
            # update records and num_categories
            self.num_categories[attributes_group_index[0]] = num_categories
            self.records[:, attributes_group_index[0]] = new_record
            
            # update decode related parameters
            if recode_times == 0:
                self.recode_significant_indices_dict[attributes_group_key] = significant_cell_indices
                self.recode_group_indices_dict[attributes_group_key] = group_cell_indices
                self.recode_views_dict[attributes_group_key] = view
        
            # construct view to synthesize dataset
            new_indicator = np.zeros(len(self.num_categories), dtype=np.uint8)
            new_indicator[attributes_group_index[0]] = 1
            new_view = View(new_indicator, self.num_categories)
            
            if num_group > group_value_threshold and attributes_group_key not in special_attribute:
                new_view.count = np.concatenate((significant_value, np.array([np.sum(view.count[group_cell_indices])])))
            else:
                new_view.count = significant_value
            
            # update synthesizing related parameters
            for view_group_name in ["A", "AGE1", "AGE2", "SL"]:
                if attributes_group_key in self.attributes_group.recode_group_key[view_group_name] \
                        or attributes_group_key in self.attributes_group.recode_single_key[view_group_name]:
                    self.views_group[view_group_name][attributes_group_key] = new_view
                    self.views_iterate_key[view_group_name].append(attributes_group_key)
                    self.views_consist_key[view_group_name].append(attributes_group_key)
                    
                    break
    
            self.logger.info("maximum remain: %s, actual remain: %s" % (num_keep_value, num_categories))