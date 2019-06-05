import logging

import numpy as np

from experiment.experiment_dpsyn import ExperimentDPSyn
from lib_dpsyn.records_update import RecordUpdate
from lib_view.view import View


class ExperimentDPSynMCF(ExperimentDPSyn):
    def __init__(self, path, anonymization, synthesizer):
        super(ExperimentDPSynMCF, self).__init__(path, anonymization, synthesizer)

        self.logger = logging.getLogger("dpsyn_mcf")
        
        self.age_bin_1 = None
        self.age_bin_2 = None
        
        self.incwage_fill_value = None

    def update_records(self, views_group_name, threshold, num_synthesize_records=None):
        self.logger.info("-" * 20 + "updating group %s" + "-" * 20, views_group_name)
        
        views_iterate_key = self.views_iterate_key[views_group_name]
        self.update_num_categories(views_group_name)
        synthesizer = RecordUpdate(self.num_categories, self.original_num_categories)
    
        if num_synthesize_records == None:
            num_synthesize_records = self.num_synthesize_records
            
        synthesizer.initialize_records(num_synthesize_records, self.num_attributes, len(views_iterate_key), self.update_iterations)
    
        alpha = 0.2
        
        count = 1
        update_round = 0
        
        while count != 0 and update_round < self.update_iterations:
            self.logger.info("Update round: %d" % (update_round,))
        
            count = 0
        
            for index, key in enumerate(views_iterate_key):
                self.logger.info("updating %s view: %s, num_key: %s" % (index, key, self.views_group[views_group_name][key].num_key))
                
                count += synthesizer.update_records_S5(self.views_group[views_group_name][key], alpha, threshold, index, update_round)
        
            update_round += 1
    
        return synthesizer
    
    def update_num_categories(self, view_group_name):
        if view_group_name == "AGE1":
            self.num_categories[self.attri_name_index_mapping["AGE"]] = self.age_bin_1.size + 1
        elif view_group_name == "AGE2":
            self.num_categories[self.attri_name_index_mapping["AGE"]] = self.age_bin_2.size + 1
    
    def update_records_fully(self, synthesizer, view_key, group_name):
        self.logger.info("update records to fully match %s marginal" % (view_key,))
    
        if view_key in self.views_group[group_name]:
            view = self.views_group[group_name][view_key]
            view_index = self.views_iterate_key[group_name].index(view_key)
        
            synthesizer.update_records_fully(view, 0.0, view_index, self.update_iterations - 1)
        else:
            self.logger.warning("view %s do not exist in the specific group" % (view_key,))

    def recode_attributes(self, threshold, city_epsilon=0, city_threshold=0):
        self.logger.info("recoding attributes")
        num_recode_group = 0
    
        for group_name in ["A", "AGE1", "AGE2"]:
            group = self.attributes_group.recode_group_key[group_name]
            
            for attributes_group_key in group:
                self.recode.attributes_group_anonymize(attributes_group_key, self.sensitivity, self.gauss_sigma)
                num_recode_group += 1
    
        for group_name in ["A", "AGE1", "AGE2"]:
            group = self.attributes_group.recode_single_key[group_name]
            
            for attribute in group:
                if attribute == "CITY":
                    if city_epsilon == 0:
                        self.recode.attributes_group_anonymize(attribute, self.sensitivity, self.gauss_sigma)
                    else:
                        self.recode.attributes_group_anonymize(attribute, self.sensitivity, self.gauss_sigma, epsilon=city_epsilon)
                else:
                    self.recode.attributes_group_anonymize(attribute, self.sensitivity, self.gauss_sigma)
                
                num_recode_group += 1
    
        self.num_records_estimation[0] /= num_recode_group
    
        for group_name in ["A", "AGE1", "AGE2"]:
            group = self.attributes_group.recode_group_key[group_name]
            
            for attributes_group_key in group:
                self.recode.attributes_recode(attributes_group_key, threshold)
    
        for group_name in ["A", "AGE1", "AGE2"]:
            group = self.attributes_group.recode_single_key[group_name]
            
            for attribute in group:
                if attribute == "CITY":
                    if city_threshold == 0:
                        self.recode.attributes_recode(attribute, threshold)
                    else:
                        self.recode.attributes_recode(attribute, city_threshold)
                else:
                    self.recode.attributes_recode(attribute, threshold)
    
        self.logger.info("recoded attributes")

    def generate_marginal(self, attributes_list, views_group_name="A", is_iterate=True, is_consist=True):
        basis = []
    
        for attribute_name in attributes_list:
            if attribute_name in self.attributes_group.recode_group_key_summary:
                attri_name = self.attributes_group.recode_group_key[views_group_name][attribute_name][0]
                basis.append(self.attri_name_index_mapping[attri_name])
            else:
                basis.append(self.attri_name_index_mapping[attribute_name])
    
        if all(self.num_categories[basis] != 0):
            view = self.anonymize_views(self.construct_views(basis))
            
            self.views_group[views_group_name][tuple(attributes_list)] = view
            
            if is_iterate:
                self.views_iterate_key[views_group_name].append(tuple(attributes_list))
                
            if is_consist:
                self.views_consist_key[views_group_name].append(tuple(attributes_list))
            
    def generate_marginal_general(self, attributes_list, records, num_categories):
        basis = []
    
        for attribute_name in attributes_list:
            basis.append(self.attri_name_index_mapping[attribute_name])

        view_indicator = np.zeros(len(num_categories), dtype=np.uint8)
        view_indicator[basis] = 1

        view = View(view_indicator, num_categories)
        view.count_records(records)
        view.calculate_count_matrix()
        
        row_nonzero_indices = []
        column_nonzero_indices = []
        
        for i in range(view.count_matrix.shape[0]):
            if np.sum(view.count_matrix[i, :]) != 0:
                row_nonzero_indices.append(i)
                
        for j in range(view.count_matrix.shape[1]):
            if np.sum(view.count_matrix[:, j]) != 0:
                column_nonzero_indices.append(j)
                
        valid_count_matrix = view.count_matrix[np.ix_(row_nonzero_indices, column_nonzero_indices)]
        
        return view, valid_count_matrix

    def onebyone_mapping_from_marginal(self, anchor_attribute, fill_attribute):
        mapping = {}
        basis = []
        basis.append(self.attri_name_index_mapping[fill_attribute])
        basis.append(self.attri_name_index_mapping[anchor_attribute])
    
        view = self.anonymize_views(self.construct_views(basis))
        view.calculate_count_matrix()
    
        anchor_index = np.where(view.attributes_index == self.attri_name_index_mapping[anchor_attribute])[0]
    
        if anchor_index == 0:
            for anchor in range(view.count_matrix.shape[0]):
                fill = np.argmax(view.count_matrix[anchor, :])
                mapping[anchor] = fill
        elif anchor_index == 1:
            for anchor in range(view.count_matrix.shape[1]):
                fill = np.argmax(view.count_matrix[:, anchor])
                mapping[anchor] = fill
    
        self.onebyone_mapping[(anchor_attribute, fill_attribute)] = mapping
        
    def key_attri_index(self, iterate_keys):
        ret_set = set()
    
        for keys in iterate_keys:
            if type(keys) is str:
                # if len(keys) == 1:
                if keys in self.attributes_group.recode_group_key_summary:
                    ret_set.update({self.attributes_group.recode_group_index[keys][0]})
                else:
                    ret_set.update({self.attri_name_index_mapping[keys]})
            elif type(keys) is tuple:
                for key in keys:
                    if key in self.attributes_group.recode_group_key_summary:
                        ret_set.update({self.attributes_group.recode_group_index[key][0]})
                    else:
                        ret_set.update({self.attri_name_index_mapping[key]})
            
        return list(ret_set)
        
        
        
    