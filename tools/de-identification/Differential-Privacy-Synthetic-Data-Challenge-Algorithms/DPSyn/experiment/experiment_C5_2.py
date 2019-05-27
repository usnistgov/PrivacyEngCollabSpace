from itertools import combinations

import numpy as np

from experiment.experiment_C5 import Experiment_C5


class Experiment_C5_2(Experiment_C5):
    def __init__(self, path, anonymization, synthesizer):
        super(Experiment_C5_2, self).__init__(path, anonymization, synthesizer)
        
        # this function specify the attributes to be compressed, do not consume privacy budget
        # the consumed privacy budget for recoded attributes are calculated in function configuration_C5_2()
        self.attributes_group.use_recode_scheme_3()
        
        # construct noisy views based on configuration A1
        # this function is the only part that touches dataset and consumes privacy budget
        self.configuration_C5_2()

        # consist noisy views
        # post-processing code
        for view_group_name in ["A", "AGE1", "AGE2", "SL"]:
            self.logger.info("consist for group %s" % (view_group_name,))
            
            self.update_num_categories(view_group_name)
            self.consist_views(self.views_group[view_group_name], self.views_consist_key[view_group_name])

        # generate synthetic dataset
        # post-processing code
        self.synthesize_records()
        
        # fill in some attributes based on mapping and decode attributes
        # post-precessing code
        self.post_processing()
        
        self.generate_submission_dataset(self.synthesized_records)
    
    def configuration_C5_2(self):
        self.epsilon_incwage_singleton = self.epsilon / 24.0
        self.epsilon_enumdist_singleton = self.epsilon / 24.0
        self.epsilon_minc_marginal = self.epsilon / 4.0
        
        self.reserve_epsilon = self.epsilon_incwage_singleton + self.epsilon_enumdist_singleton + self.epsilon_minc_marginal
        self.remain_epsilon = self.epsilon - self.reserve_epsilon
        
        ####### calculate algorithm parameters and preprocess data ########
        # calculate the noise variance for each marginal based on Renyi-DP
        if self.epsilon >= 1.0:
            self.calculate_noise_parameter(203)
        else:
            self.calculate_noise_parameter(193)
        
        # preprocess attributes
        self.geo_attributes_mapping = self.preprocess.refine_geo_attributes()
        
        ################## recode attributes groups ########################
        # Totally 26 marginals
        
        threshold = max(4.5 * self.gauss_sigma, 800)
        self.recode_attributes(threshold)
        
        ###################################### generate marginals #################################
        # generate income related marginals
        # we have reserved privacy budget for INCWAGE related marginals,
        # thus do not count as the number of marginals to calculate sigma in function calculate_noise_parameter()
        self.generate_incwage_marginal()

        ########################################## Group A #############################################
        # Totally 4 marginals
        
        ##### generate other misc information 1 related marginals (1) #####
        self.generate_marginal(["SPL_GQ_GQF", "GQTYPED"])

        ##### generate race related marginals (3) #####
        attributes_list = ["RACED", "SPANN", "HISPAND"]
        for attributes_group_key in combinations(attributes_list, 2):
            self.generate_marginal(attributes_group_key)

        ########################################## Group AGE1 #############################################
        # Totally 6 marginal
        
        # handle AGE attributes (1)
        age_index = self.attri_name_index_mapping["AGE"]
        
        self.age_singleton = self.anonymize_views(self.construct_views([age_index]))
        self.age_singleton.non_negativity("N1")
        self.age_singleton.calculate_normalize_count()
        
        age_record = np.copy(self.records[:, age_index])
        self.age_bin_1 = self.preprocess.bucketize_age_1()
        
        # generate individual information 1 related marginals (2)
        self.generate_marginal(["BPL", "AGE"], views_group_name="AGE1")
        self.generate_marginal(["CITIZEN"], views_group_name="AGE1", is_iterate=False)

        # generate individual information 2 related marginals (3)
        attributes_list = ["FBPL", "MBPL", "AGE"]

        for attributes_group_key in combinations(attributes_list, 2):
            self.generate_marginal(attributes_group_key, views_group_name="AGE1")

        ########################################## Group AGE2 #############################################
        # Totally 145 marginals
        
        ###### handle AGE attributes #####
        self.records[:, age_index] = age_record
        self.age_bin_2 = self.preprocess.bucketize_age_2()

        ##### generate individual information 3 related marginals (6) #####
        self.generate_marginal(["AGE", "RESPONDT"], views_group_name="AGE2")
        self.generate_marginal(["AGE", "SCHOOL"], views_group_name="AGE2")
        self.generate_marginal(["AGE", "MARST"], views_group_name="AGE2")
        self.generate_marginal(["AGE", "NCHLT5"], views_group_name="AGE2")
        self.generate_marginal(["SCHOOL", "MARST", "NCHLT5"], views_group_name="AGE2")
        self.generate_marginal(["SCHOOL", "MARST", "RESPONDT"], views_group_name="AGE2")
        
        ##### generate work related marginals (55 + 2 = 57) #####
        attributes_list = ["EDUCD", "INCWAGE", "LF_INCNON", "EMPSTATD", "CLASSWKRD", "OCC1950",
                           "IND1950", "WKSWORK2", "HRSWORK2", "AGE"]

        for attributes_group_key in combinations(attributes_list, 2):
            self.generate_marginal(attributes_group_key, views_group_name="AGE2")
            
        self.generate_work_time_marginal()

        ##### generate geo-spatial related marginals (26) #####
        # we have reserved privacy budget for ENUMDIST related marginals,
        # thus do not count as the number of marginals to calculate sigma in function calculate_noise_parameter()
        self.generate_enumdist_marginal()
        
        attributes_list = ["METAREAD", "UR_FA_MT", "CITY", "WARD", "COUNTY", "ENUMDIST"]
        for attributes_group_key in combinations(attributes_list, 2):
            self.generate_marginal(attributes_group_key, views_group_name="AGE2")

        self.generate_marginal(["CITYPOP", "CITY"], views_group_name="AGE2")
        self.generate_marginal(["CITYPOP", "COUNTY"], views_group_name="AGE2")

        self.onebyone_mapping_from_marginal("COUNTY", "SEA")
        self.generate_marginal(["COUNTY", "SUPDIST"], views_group_name="AGE2", is_iterate=False, is_consist=False)
        self.generate_marginal(["CITYPOP", "URBPOP"], views_group_name="AGE2", is_iterate=False, is_consist=True)

        ##### generate migration related marginals (28) #####
        attributes_list = ["MIGRATE", "MIGPLAC5", "MIGSEA5", "MIGMET5", "MIGCITY5", "MIGCOUNTY",
                           "SAME_MIGT"]

        for attributes_group_key in combinations(attributes_list, 2):
            self.generate_marginal(attributes_group_key, views_group_name="AGE2")

        ##### inter-group marginals for geo-spatial and migration attributes (15) #####
        attributes_list = ["MIGPLAC5", "MIGSEA5", "MIGMET5", "MIGCITY5", "MIGCOUNTY"]
        for attri_group_1 in attributes_list:
            for attri_group_2 in ["CITY", "COUNTY", "AGE"]:
                self.generate_marginal([attri_group_1, attri_group_2], views_group_name="AGE2")

        ##### generate other misc information 2 related marginals (7) #####
        self.generate_rent_marginal()
        self.generate_valueh_marginal()
        self.generate_famsize_marginal()

        self.generate_marginal(["OWNERSHPD", "RENT"], views_group_name="AGE2")
        self.generate_marginal(["OWNERSHPD", "VALUEH"], views_group_name="AGE2")
        self.generate_marginal(["OWNERSHPD", "FAMSIZE"], views_group_name="AGE2")
        self.generate_marginal(["OWNERSHPD", "FAMSIZE"], views_group_name="AGE2")

        #### generate inter-group marginals (6) #####
        self.generate_marginal(["FAMSIZE", "AGE"], views_group_name="AGE2")
        self.generate_marginal(["OWNERSHPD", "MIGRATE"], views_group_name="AGE2")
        
        self.generate_marginal(["SEX", "LF_INCNON"], views_group_name="AGE2")
        self.generate_marginal(["SEX", "EMPSTATD"], views_group_name="AGE2")
        self.generate_marginal(["SEX", "OCC1950"], views_group_name="AGE2")
        self.generate_marginal(["SEX", "IND1950"], views_group_name="AGE2")

        ########################################## Group SL #############################################
        # Totally 12 / 22 marginals
        
        ##### recode (4) ######
        self.recode_sample_line_attributes()
        
        ##### generate sample line attributes #####
        # 1-way marginals (8)
        attributes_list = ["SSENROLL", "MTONGUED", "CHBORN", "AGEMARR", "NATIVITY", "MARRNO"]
        for attributes_group_key in attributes_list:
            self.generate_marginal([attributes_group_key], views_group_name="SL")
            
        self.generate_marginal(["VET1940", "VETSTATD", "VETPER"], views_group_name="SL")
        self.generate_marginal(["VETCHILD", "VETWWI"], views_group_name="SL")
        
        # 2-way marginals (10)
        if self.epsilon >= 1.0:
            attributes_list = ["SSENROLL", "UOCC", "UOCC95", "UIND", "UCLASSWK"]
            for attributes_group_key in combinations(attributes_list, 2):
                self.generate_marginal(attributes_group_key, views_group_name="SL")
    
    
