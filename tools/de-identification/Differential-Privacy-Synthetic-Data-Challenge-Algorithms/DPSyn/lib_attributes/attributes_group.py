

class AttributeGroup:
    def __init__(self, attri_name_index_mapping):
        self.attri_name_index_mapping = attri_name_index_mapping

    def use_recode_scheme_3(self):
        self.recode_group_key = {
            "A": {
                "SPL_GQ_GQF": ["SPLIT", "GQ", "GQFUNDS"],
                "SPANN": ["SPANNAME", "HISPRULE"],
            },
            "AGE1": {
            },
            "AGE2": {
                "UR_FA_MT": ["URBAN", "FARM", "METRO"],
                "MIGRATE": ["MIGRATE5", "MIGRATE5D"],
                "SAME_MIGT": ["SAMESEA5", "SAMEPLAC", "MIGTYPE5"],
                # "LF_SEX_INCNON": ["LABFORCE", "SEX", "INCNONWG"],
                "LF_INCNON": ["LABFORCE", "INCNONWG"],
            },
            "SL": {
                # "VETERAN": ["VETPER", "VET1940", "VETSTATD"],
                # "VETC_VETW": ["VETWWI", "VETCHILD"],
            }
        }
        self.recode_single_key = {
            "A": {
                "AGEMONTH",
                "DURUNEMP",
                "GQTYPED",
                
                "RACED",
                "HISPAND",
            },
            "AGE1": {
                "BPL",
                "FBPL",
                "MBPL"
            },
            "AGE2": {
                # "METAREAD",
                # "CITY",
                "CITYPOP",
                "WARD",
                # "ENUMDIST",
                "MIGPLAC5",
                "MIGSEA5",
                "MIGMET5",
                "MIGCITY5",
                "MIGCOUNTY",
                
                "EDUCD",
                "EMPSTATD",
                "CLASSWKRD",
                "OCC1950",
                "IND1950",
            },
            "SL": {
                "UOCC",
                "UOCC95",
                "UIND",
                "UCLASSWK"
            }
        }
    
        self.recode_group_index = {}
    
        self.translate_recode_group()
        self.translate_recode_single()
        
    def translate_recode_group(self):
        self.recode_group_key_summary = []
        
        for _, group in self.recode_group_key.items():
            for key, value in group.items():
                index_list = []
                
                for attribute_name in value:
                    index_list.append(self.attri_name_index_mapping[attribute_name])
                
                self.recode_group_index[key] = index_list
                self.recode_group_key_summary.append(key)
        
    def translate_recode_single(self):
        for _, group in self.recode_single_key.items():
            for attribute_name in group:
                self.recode_group_index[attribute_name] = [self.attri_name_index_mapping[attribute_name]]
        