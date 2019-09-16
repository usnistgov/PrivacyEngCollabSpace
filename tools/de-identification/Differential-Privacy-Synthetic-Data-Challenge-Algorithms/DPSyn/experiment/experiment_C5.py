import numpy as np

from experiment.experiment_dpsyn_mcf import ExperimentDPSynMCF
from lib_view.view import View


class Experiment_C5(ExperimentDPSynMCF):
    def __init__(self, path, anonymization, synthesizer):
        super(Experiment_C5, self).__init__(path, anonymization, synthesizer)
        
        self.age_singleton = None
        self.geo_attributes_mapping = None
        
        self.epsilon_enumdist_singleton = 0.0
        self.epsilon_incwage_singleton = 0.0
        self.epsilon_minc_marginal = 0.0
    
    def synthesize_records(self):
        self.logger.info("synthesizing records")

        ##################### iteratively synthesize data ####################
        records = np.zeros([self.num_synthesize_records, self.num_attributes], dtype=np.uint32)

        # iteratively update marginals in group
        attribute_index_dict = {}
        error_tracker = np.zeros([1, self.update_iterations * 2])

        for views_group_name in ["A", "AGE1", "AGE2"]:
            attri_index = self.key_attri_index(self.views_iterate_key[views_group_name])
            attribute_index_dict[views_group_name] = attri_index
            synthesizer = self.update_records(views_group_name, 0.0)

            # save age records, or it will be rewrite by AGE2
            if views_group_name == "AGE1":
                # self.update_records_fully(synthesizer, ("BPL", "AGE"), "AGE1")
                self.age_records = np.copy(synthesizer.records[:, self.attri_name_index_mapping["AGE"]])
            
            elif views_group_name == "AGE2":
                self.update_records_fully(synthesizer, ("INCWAGE", "SEX", "CITY"), "AGE2")
                # self.update_records_fully(synthesizer, ("CITYPOP", "CITY"), "AGE2")
            
            records[:, attri_index] = synthesizer.records[:, attri_index]
            error_tracker = np.concatenate((error_tracker, synthesizer.error_tracker))

        attri_index = self.key_attri_index(self.views_iterate_key["SL"])
        attribute_index_dict["SL"] = attri_index
        num_records = (self.views_group["SL"][("SSENROLL",)].sum / self.views_group["AGE1"][("CITIZEN",)].sum) * self.num_synthesize_records
        synthesizer = self.update_records("SL", 0.0, num_synthesize_records=int(num_records))
        self.postprocess.decode_anchor_attributes(synthesizer.records, ["SL"])

        sl_records = synthesizer.records[:, attri_index]

        self.join_records(records, sl_records, attribute_index_dict)
        
    def join_records(self, records, sl_records, attribute_index_dict):
        self.logger.info("joining records")
        
        self.synthesized_records = np.zeros([self.num_synthesize_records, self.num_attributes], dtype=np.uint32)
        
        ####################################### join group A ###################################
        attri_index = attribute_index_dict["A"]
        self.synthesized_records[:, attri_index] = records[:, attri_index]
        
        np.random.shuffle(self.synthesized_records)

        ####################################### join group AGE1 ###################################
        attri_index = attribute_index_dict["AGE1"]
        age_index = self.attri_name_index_mapping["AGE"]
        
        self.synthesized_records[:, attri_index] = records[:, attri_index]
        self.synthesized_records[:, age_index] = self.age_records

        ####################################### join group AGE2 ###################################
        attri_index = attribute_index_dict["AGE2"]
        self.postprocess.decode_ordinal_attributes(records, self.age_singleton.normalize_count, self.age_bin_2, age_index)

        record = np.copy(self.synthesized_records[:, age_index])
        age_bin_1_remain_indices = np.zeros(0, dtype=np.uint32)
        age_bin_2_remain_indices = np.zeros(0, dtype=np.uint32)

        for value_1 in range(1, self.age_bin_1.size + 1):
            age_bin_1_indices = np.where(record == value_1)[0]
            age_bin_2_indices = np.zeros(0, dtype=np.uint32)

            if value_1 < self.age_bin_1.size:
                value_2_list = np.arange(self.age_bin_1[value_1 - 1], self.age_bin_1[value_1])
            else:
                value_2_list = np.arange(self.age_bin_1[value_1 - 1], self.age_singleton.num_key)

            for value_2 in value_2_list:
                indices = np.where(records[:, age_index] == value_2)[0]
                age_bin_2_indices = np.union1d(age_bin_2_indices, indices)

            # join procedure
            if age_bin_1_indices.size >= age_bin_2_indices.size:
                self.synthesized_records[np.ix_(age_bin_1_indices[:age_bin_2_indices.size], attri_index)] = records[np.ix_(age_bin_2_indices, attri_index)]
                age_bin_1_remain_indices = np.union1d(age_bin_1_remain_indices, age_bin_1_indices[age_bin_2_indices.size:])
            else:
                self.synthesized_records[np.ix_(age_bin_1_indices, attri_index)] = records[np.ix_(age_bin_2_indices[:age_bin_1_indices.size], attri_index)]
                age_bin_2_remain_indices = np.union1d(age_bin_2_remain_indices, age_bin_2_indices[age_bin_1_indices.size:])

        self.synthesized_records[np.ix_(age_bin_1_remain_indices, attri_index)] = records[np.ix_(age_bin_2_remain_indices[: age_bin_1_remain_indices.size], attri_index)]
        self.logger.warning("age indices inconsist number is %s" % (age_bin_2_remain_indices.size - age_bin_1_remain_indices.size,))

        age_bin_1_indices_0 = np.where(record == 0)[0]
        self.synthesized_records[np.ix_(age_bin_1_indices_0, attri_index)] = records[np.ix_(age_bin_2_remain_indices[age_bin_1_remain_indices.size:], attri_index)]

        np.random.shuffle(self.synthesized_records)
        
        ####################################### join group SL ###################################
        attri_index = attribute_index_dict["SL"]
        default_value, default_attri_index = self.calculate_sample_line_default()
        slrec_index = self.attri_name_index_mapping["SLREC"]

        fbpl_indices = np.where(self.synthesized_records[:, self.attri_name_index_mapping["FBPL"]] == 0)[0]
        mbpl_indices = np.where(self.synthesized_records[:, self.attri_name_index_mapping["MBPL"]] == 0)[0]
        sample_line_indices_candidate = np.setdiff1d(np.arange(self.num_synthesize_records), np.union1d(fbpl_indices, mbpl_indices))
        
        if sample_line_indices_candidate.size != 0:
            sample_line_indices = np.random.choice(sample_line_indices_candidate, sl_records.shape[0], replace=False)
            non_sample_line_indices = np.setdiff1d(np.arange(self.num_synthesize_records), sample_line_indices)
    
            self.synthesized_records[np.ix_(sample_line_indices, attri_index)] = sl_records
            self.synthesized_records[sample_line_indices, slrec_index] = 1
            
            self.synthesized_records[np.ix_(non_sample_line_indices, default_attri_index)] = np.tile(default_value, (non_sample_line_indices.size, 1))
            self.synthesized_records[non_sample_line_indices, slrec_index] = 0
        else:
            self.synthesized_records[:, default_attri_index] = np.tile(default_value, (self.num_synthesize_records, 1))
            self.synthesized_records[:, slrec_index] = 0

        np.random.shuffle(self.synthesized_records)
        
    def calculate_sample_line_default(self):
        self.sample_line_default = {
            "SSENROLL": 0,
            "UOCC": 999,
            "UOCC95": 999,
            "UIND": 999,
            "UCLASSWK": 0,
            "MTONGUED": 0,
            "VET1940": 0,
            "VETSTATD": 0,
            "VETPER": 0,
            "VETCHILD": 0,
            "VETWWI": 0,
            "CHBORN": 0,
            "AGEMARR": 0,
            "NATIVITY": 0,
            "MARRNO": 0
        }
        default_value = np.zeros(len(self.sample_line_default), dtype=np.uint32)
        default_attri_index = np.zeros(len(self.sample_line_default), dtype=np.uint32)
        i = 0
        
        for attri_name in self.sample_line_default:
            if attri_name in self.code_mapping:
                default_value[i] = np.where(self.code_mapping[attri_name] == self.sample_line_default[attri_name])[0]
                default_attri_index[i] = self.attri_name_index_mapping[attri_name]
            else:
                default_value[i] = self.sample_line_default[attri_name]
                default_attri_index[i] = self.attri_name_index_mapping[attri_name]
                
            i += 1
                
        return default_value, default_attri_index
    
    def post_processing(self):
        # decode incwage and fill sea, supdist
        self.postprocess.decode_incwage_C5(self.synthesized_records, self.incwage_singleton, self.incwage_bin)
        self.postprocess.fill_onebyone_mapping_attributes(self.synthesized_records)
        self.postprocess.fill_supdist_attribute(self.synthesized_records, self.gauss_sigma)
        
        # decode attributes
        self.postprocess.decode_anchor_attributes(self.synthesized_records, ["A", "AGE1", "AGE2"])
        self.postprocess.decode_ordinal_attributes(self.synthesized_records)
        self.postprocess.decode_geo_attributes(self.synthesized_records, self.geo_attributes_mapping)
        
        # fill attributes from mapping
        self.postprocess.load_mapping_data()
        # pair mapping and general detail mapping cannot change order (EDUCD -> HIGRADED)
        self.postprocess.fill_pair_mapping_attributes(self.synthesized_records)
        self.postprocess.fill_general_from_detail(self.synthesized_records)

        # fill attributes
        self.postprocess.fill_bpl_attributes(self.synthesized_records)
        self.postprocess.fill_geo_attributes(self.synthesized_records)
        self.postprocess.fill_citizen_attribute(self.synthesized_records)
        
        self.logger.info("synthesized records")
    
    def recode_sample_line_attributes(self):
        slrec_index = self.attri_name_index_mapping["SLREC"]
        indices_sample = np.where(self.records[:, slrec_index] == 1)[0]
        
        # only remain the records for slrec=1, after this step, self.records should not be used
        self.records = self.records[indices_sample]
        self.recode.records = self.records
        threshold = max(3.0 * self.gauss_sigma, 800)

        for attributes_group_key in self.attributes_group.recode_group_key["SL"]:
            self.recode.attributes_group_anonymize(attributes_group_key, self.sensitivity, self.gauss_sigma)

        for attributes_group_key in self.attributes_group.recode_group_key["SL"]:
            self.recode.attributes_recode(attributes_group_key, threshold)
            
        for attribute in self.attributes_group.recode_single_key["SL"]:
            self.recode.attributes_group_anonymize(attribute, self.sensitivity, self.gauss_sigma)

        for attribute in self.attributes_group.recode_single_key["SL"]:
            self.recode.attributes_recode(attribute, threshold)
    
    def generate_work_time_marginal(self):
        for attribute_name in ["WKSWORK1", "HRSWORK1"]:
            attribute_index = self.attri_name_index_mapping[attribute_name]
            view = self.anonymize_views(self.construct_views([attribute_index]))
        
            view.non_negativity()
            view.calculate_normalize_count()
        
            self.ordinal_views_dict[attribute_name] = view
            
            if attribute_name == "WKSWORK1":
                self.ordinal_bin_dict[attribute_name] = np.array([0, 1, 14, 27, 40, 48, 50])
            elif attribute_name == "HRSWORK1":
                self.ordinal_bin_dict[attribute_name] = np.array([0, 1, 15, 30, 35, 40, 41, 49, 60])

    def generate_enumdist_marginal(self):
        attribute_index = self.attri_name_index_mapping["ENUMDIST"]
        view = self.anonymize_views(self.construct_views([attribute_index]), epsilon=self.epsilon_enumdist_singleton)
    
        if self.epsilon <= 0.2:
            valid_value_index = np.arange(10, view.num_key, 10)
            invalid_value_index = np.setdiff1d(np.arange(view.num_key), valid_value_index)
            view.count[invalid_value_index] = 0.0
        
        view.non_negativity()
        view.calculate_normalize_count()
    
        self.ordinal_views_dict["ENUMDIST"] = view
        self.ordinal_bin_dict["ENUMDIST"] = self.preprocess.bucketize_enumdist()
    
    def generate_rent_marginal(self):
        attribute_index = self.attri_name_index_mapping["RENT"]
        view = self.anonymize_views(self.construct_views([attribute_index]))
        
        if self.epsilon <= 0.2:
            view.count[1001: 9998] = 0
        
        view.non_negativity()
        view.calculate_normalize_count()
    
        self.ordinal_views_dict["RENT"] = view
        self.ordinal_bin_dict["RENT"] = self.preprocess.bucketize_rent()

    def generate_valueh_marginal(self):
        attribute_index = self.attri_name_index_mapping["VALUEH"]
        view = self.anonymize_views(self.construct_views([attribute_index]))
        
        if self.epsilon <= 0.2:
            valid_value_index = np.arange(0, 50001, 50)
            invalid_value_index = np.setdiff1d(np.arange(9999998), valid_value_index)
            view.count[invalid_value_index] = 0.0
        else:
            view.count[50001: 9999998] = 0.0
    
        view.non_negativity()
        view.calculate_normalize_count()
    
        self.ordinal_views_dict["VALUEH"] = view
        self.ordinal_bin_dict["VALUEH"] = self.preprocess.bucketize_valueh()

    def generate_famsize_marginal(self):
        attribute_index = self.attri_name_index_mapping["FAMSIZE"]
        view = self.anonymize_views(self.construct_views([attribute_index]))
    
        view.count[31:] = 0.0
    
        view.non_negativity()
        view.calculate_normalize_count()
    
        self.ordinal_views_dict["FAMSIZE"] = view
        self.ordinal_bin_dict["FAMSIZE"] = self.preprocess.bucketize_famsize()
        
    def generate_incwage_marginal(self):
        self.logger.info("generating incwage marginal")

        ########################### calculate singleton ##########################
        attribute_index = self.attri_name_index_mapping["INCWAGE"]
        view = self.anonymize_views(self.construct_views([attribute_index]), epsilon=self.epsilon_incwage_singleton)

        view.count[5001: 999998] = 0.0
        
        self.incwage_singleton = view
        
        ########################### buketize INCWAGE ####################################
        if self.epsilon >= 1.0:
            self.incwage_bin = self.preprocess.bucketize_incwage_4()
        elif self.epsilon > 0.2 and self.epsilon < 1.0:
            self.incwage_bin = self.preprocess.bucketize_incwage_5()
        elif self.epsilon <= 0.2:
            self.incwage_bin, self.original_incwage_record = self.preprocess.bucketize_incwage_6()
        
        ################ calculate 3-way marginal for INCWAGE, SEX, CITY ###############
        basis = []

        for attribute_name in ["INCWAGE", "SEX", "CITY"]:
            basis.append(self.attri_name_index_mapping[attribute_name])

        self.minc_marginal = self.anonymize_views(self.construct_views(basis), epsilon=self.epsilon_minc_marginal)
        self.minc_marginal.calculate_tuple_key()
        
        # after bucketizing, value 0 do not exist since it corresponds to negative value
        cell_indices = np.where(self.minc_marginal.tuple_key[:, 2] == 0)[0]
        self.minc_marginal.count[cell_indices] = 0.0
        
        self.minc_marginal.non_negativity()
        self.minc_marginal.calculate_normalize_count()

        self.views_group["AGE2"][("INCWAGE", "SEX", "CITY")] = self.minc_marginal
        self.views_iterate_key["AGE2"].append(("INCWAGE", "SEX", "CITY"))
        
        ########################## consist between marginals ###########################
        self.consist_incwage()
        
        ########################### get finer-grained INCWAGE ##############################
        if self.epsilon <= 0.2:
            self.finer_minc_marginal()

    def consist_incwage(self):
        self.logger.info("consisting incwage related marginals")
        
        def consist():
            minc_count = np.zeros(self.incwage_bin.size + 1)
            
            for index, value in enumerate(range(minc_count.size)):
                cell_indices = np.where(self.minc_marginal.tuple_key[:, 2] == value)[0]
                minc_count[index] = np.sum(self.minc_marginal.count[cell_indices])
                
            for index, value in enumerate(range(1, minc_count.size)):
                if value < minc_count.size - 2:
                    indices = np.arange(self.incwage_bin[value - 1], self.incwage_bin[value])
                elif value == minc_count.size - 2:
                    indices = np.arange(self.incwage_bin[value - 1], 5001)
                else:
                    indices = np.array([999998])
                    
                singleton_count = np.sum(self.incwage_singleton.count[indices])
                self.incwage_singleton.count[indices] += (minc_count[index + 1] - singleton_count) / indices.size
                
        for iteration in range(10):
            self.logger.info("iteration %s" % (iteration,))

            self.incwage_singleton.non_negativity()
            
            consist()
            
            if not (self.incwage_singleton.count < 0.0).any():
                break
                
        self.incwage_singleton.calculate_normalize_count()

    def finer_minc_marginal(self):
        ########################## get finer bucketized INCWAGE ###########################
        incwage_index = self.attri_name_index_mapping["INCWAGE"]
        self.records[:, incwage_index] = self.original_incwage_record
        incwage_finer_bin = self.preprocess.bucketize_incwage_7()
        
        finer_dist = [0.0]
        
        for index in range(incwage_finer_bin.size):
            if index < incwage_finer_bin.size - 1:
                finer_dist.append(np.sum(self.incwage_singleton.count[incwage_finer_bin[index]: incwage_finer_bin[index + 1]]))
            else:
                finer_dist.append(np.sum(self.incwage_singleton.count[incwage_finer_bin[index: ]]))
        
        finer_dist = np.array(finer_dist)
        
        ########################## update minc_marginal ###########################
        basis = []
    
        for attribute_name in ["INCWAGE", "SEX", "CITY"]:
            basis.append(self.attri_name_index_mapping[attribute_name])
            
        indicator = np.zeros(len(self.num_categories), dtype=np.uint8)
        indicator[basis] = 1
        view = View(indicator, self.num_categories)
        view.calculate_tuple_key()
        
        for incwage_value in range(1, 7):
            minc_cell_indices = np.where(self.minc_marginal.tuple_key[:, -1] == incwage_value)[0]
            
            if incwage_value in [1]:
                view_cell_indices = np.where(view.tuple_key[:, -1] == 1)[0]
                view.count[view_cell_indices] = self.minc_marginal.count[minc_cell_indices]
            elif incwage_value in [2, 3, 4, 5]:
                finer_dist_index = [2 * (incwage_value - 1), 2 * (incwage_value - 1) + 1]
                view_dist = []

                if np.sum(finer_dist[finer_dist_index]) != 0:
                    ratio = finer_dist[finer_dist_index] / np.sum(finer_dist[finer_dist_index])
                else:
                    ratio = np.array([0.5, 0.5])
                
                for index in minc_cell_indices:
                    view_dist.append(self.minc_marginal.count[index] * ratio[0])
                    view_dist.append(self.minc_marginal.count[index] * ratio[1])
                
                view_cell_indices = np.where(view.tuple_key[:, -1] == finer_dist_index[0])[0]
                view_cell_indices = np.union1d(view_cell_indices, np.where(view.tuple_key[:, -1] == finer_dist_index[1])[0])
                view.count[view_cell_indices] = view_dist
                
            elif incwage_value in [6]:
                view_cell_indices = np.where(view.tuple_key[:, -1] == 10)[0]
                view.count[view_cell_indices] = self.minc_marginal.count[minc_cell_indices]
                
        self.minc_marginal = view
        self.minc_marginal.calculate_normalize_count()
        
        self.views_group["AGE2"][("INCWAGE", "SEX", "CITY")] = self.minc_marginal
        self.views_iterate_key["AGE2"].append(("INCWAGE", "SEX", "CITY"))
        self.incwage_bin = incwage_finer_bin

