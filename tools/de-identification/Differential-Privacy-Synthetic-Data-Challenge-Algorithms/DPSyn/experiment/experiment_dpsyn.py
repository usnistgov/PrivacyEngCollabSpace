import logging
from collections import defaultdict

import numpy as np

from experiment.experiment import Experiment
from lib_view.view import View
from lib_view.consistent import Consistenter
from lib_composition.advanced_composition import AdvancedComposition
from lib_attributes.attributes_recode import RecodeAttribute
from lib_attributes.attributes_group import AttributeGroup
from lib_attributes.attributes_preprocess import PreprocessAttribute
from lib_attributes.attributes_postprocess import PostprocessAttribute


class ExperimentDPSyn(Experiment):
    def __init__(self, path, anonymization, synthesizer):
        super(ExperimentDPSyn, self).__init__(path, anonymization)

        self.logger = logging.getLogger("dpsyn")

        self.num_synthesize_records = synthesizer["num_records"]
        self.consist_iterations = synthesizer["consist_iterations"]
        self.update_iterations = synthesizer["update_iterations"]
        
        self.reserve_epsilon = 0.0
        self.remain_epsilon = self.epsilon

        self.attributes_group = AttributeGroup(self.attri_name_index_mapping)
        
        self.views_group = defaultdict(dict)
        self.views_iterate_key = defaultdict(list)
        self.views_consist_key = defaultdict(list)
        self.num_records_estimation = [0.0]

        self.ordinal_views_dict = {}
        self.ordinal_bin_dict = {}
        
        self.recode_significant_indices_dict = {}
        self.recode_group_indices_dict = {}
        self.recode_views_dict = {}
        
        self.onebyone_mapping = {}
        
        self.common_parameters = {
            "recode_significant_indices_dict": self.recode_significant_indices_dict,
            "recode_group_indices_dict": self.recode_group_indices_dict,
            "recode_views_dict": self.recode_views_dict,
            "views_group": self.views_group,
            "views_iterate_key": self.views_iterate_key,
            "views_consist_key": self.views_consist_key,
            "ordinal_views_dict": self.ordinal_views_dict,
            "ordinal_bin_dict": self.ordinal_bin_dict,
            "attributes_group": self.attributes_group,
            "num_records_estimation": self.num_records_estimation,
            "epsilon": self.epsilon,
            "code_mapping": self.code_mapping,
            "attri_name_index_mapping": self.attri_name_index_mapping,
            "specs_path": self.specs_path,
            "incwage_bin_value": [],
            "onebyone_mapping": self.onebyone_mapping
        }
        
        self.preprocess = PreprocessAttribute(self.records, self.num_categories, self.common_parameters)
        self.recode = RecodeAttribute(self.records, self.num_categories, self.common_parameters)
        self.postprocess = PostprocessAttribute(self.num_categories, self.common_parameters)
        
    def calculate_noise_parameter(self, num_views):
        composition = AdvancedComposition()
        
        self.gauss_sigma = composition.gauss_renyi(self.remain_epsilon, self.delta, self.sensitivity, num_views)
        self.laplace_epsilon = self.epsilon / num_views
            
        self.logger.info("sigma = %s" % (self.gauss_sigma,))
    
    def construct_views(self, basis):
        view_attri = []
        
        for bas in basis:
            view_attri.append(self.dataset_header[bas])
        
        self.logger.info("constructing %s" % (tuple(view_attri),))

        view_indicator = np.zeros(len(self.num_categories), dtype=np.uint8)
        view_indicator[basis] = 1
            
        view = View(view_indicator, self.num_categories)
        view.count_records(self.records)
    
        return view
    
    def anonymize_views(self, view, epsilon=0.0):
        self.logger.info("anonymizing views")

        if epsilon != 0.0:
            view.count += np.random.laplace(scale=self.sensitivity / epsilon, size=view.num_key)
        else:
            view.count += np.random.normal(scale=self.gauss_sigma, size=view.num_key)
        
        return view
        
    def consist_views(self, views, consist_key):
        self.logger.info("consisting views")
        
        consist_views = {}
        
        for key in consist_key:
            consist_views[key] = views[key]
        
        consist_parameters = {
            "consist_iterations": self.consist_iterations
        }
        
        consistenter = Consistenter(consist_views, self.num_categories, consist_parameters)
        consistenter.consist_views()
        
        self.logger.info("consisted views")

