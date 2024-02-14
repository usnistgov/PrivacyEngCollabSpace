import numpy as np

from lib_view.non_negativity import NonNegativity


class View:
    def __init__(self, indicator, num_categories):
        self.indicator = indicator
        self.num_categories = num_categories
        
        self.num_key = np.product(self.num_categories[np.nonzero(self.indicator)[0]])
        self.num_attributes = self.indicator.shape[0]
        self.ways = np.count_nonzero(self.indicator)
        
        self.encode_num = np.zeros(self.ways, dtype=np.uint32)
        self.cum_mul = np.zeros(self.ways, dtype=np.uint32)
        self.attributes_index = np.nonzero(self.indicator)[0]
        
        self.count = np.zeros(self.num_key)

        self.calculate_encode_num(self.num_categories)

    ########################################### general functions ####################################
    def calculate_encode_num(self, num_categories):
        if self.ways != 0:
            categories_index = self.attributes_index
            
            categories_num = num_categories[categories_index]
            categories_num = np.roll(categories_num, 1)
            categories_num[0] = 1
            self.cum_mul = np.cumprod(categories_num)
    
            categories_num = num_categories[categories_index]
            categories_num = np.roll(categories_num, self.ways - 1)
            categories_num[-1] = 1
            categories_num = np.flip(categories_num)
            self.encode_num = np.flip(np.cumprod(categories_num))
    
    def calculate_tuple_key(self):
        self.tuple_key = np.zeros([self.num_key, self.ways], dtype=np.uint32)
        
        if self.ways != 0:
            for i in range(self.attributes_index.shape[0]):
                index = self.attributes_index[i]
                categories = np.arange(self.num_categories[index])
                column_key = np.tile(np.repeat(categories, self.encode_num[i]), self.cum_mul[i])
                
                self.tuple_key[:, i] = column_key
        else:
            self.tuple_key = np.array([0], dtype=np.uint32)
            self.num_key = 1

    def count_records(self, records):
        encode_records = np.matmul(records[:, self.attributes_index], self.encode_num)
        encode_key, count = np.unique(encode_records, return_counts=True)

        indices = np.where(np.isin(np.arange(self.num_key), encode_key))[0]
        self.count[indices] = count
        
    def calculate_normalize_count(self):
        if np.sum(self.count) == 0:
            self.normalize_count = self.count
        else:
            self.normalize_count = self.count / np.sum(self.count)
        
        return self.normalize_count
    
    def calculate_count_matrix(self):
        shape = []
        
        for attri in self.attributes_index:
            shape.append(self.num_categories[attri])
            
        self.count_matrix = np.copy(self.count).reshape(tuple(shape))
        
        return self.count_matrix
        
    def reserve_original_count(self):
        self.original_count = self.count
    
    def get_sum(self):
        self.sum = np.sum(self.count)

    def generate_attributes_index_set(self):
        self.attributes_set = set(self.attributes_index)

    ################################### functions for outside invoke #########################
    def calculate_encode_num_general(self, attributes_index):
        categories_index = attributes_index
    
        categories_num = self.num_categories[categories_index]
        categories_num = np.roll(categories_num, attributes_index.size - 1)
        categories_num[-1] = 1
        categories_num = np.flip(categories_num)
        encode_num = np.flip(np.cumprod(categories_num))
        
        return encode_num
    
    def count_records_general(self, records):
        count = np.zeros(self.num_key)
        
        encode_records = np.matmul(records[:, self.attributes_index], self.encode_num)
        encode_key, value_count = np.unique(encode_records, return_counts=True)

        indices = np.where(np.isin(np.arange(self.num_key), encode_key))[0]
        count[indices] = value_count
        
        return count
        
    def calculate_normalize_count_general(self, count):
        return count / np.sum(count)

    def calculate_count_matrix_general(self, count):
        shape = []
    
        for attri in self.attributes_index:
            shape.append(self.num_categories[attri])
    
        return np.copy(count).reshape(tuple(shape))
    
    def calculate_tuple_key_general(self, unique_value_list):
        self.tuple_key = np.zeros([self.num_key, self.ways], dtype=np.uint32)
    
        if self.ways != 0:
            for i in range(self.attributes_index.shape[0]):
                categories = unique_value_list[i]
                column_key = np.tile(np.repeat(categories, self.encode_num[i]), self.cum_mul[i])
            
                self.tuple_key[:, i] = column_key
        else:
            self.tuple_key = np.array([0], dtype=np.uint32)
            self.num_key = 1

    def project_from_bigger_view_general(self, bigger_view):
        encode_num = np.zeros(self.num_attributes, dtype=np.uint32)
        encode_num[self.attributes_index] = self.encode_num
        encode_num = encode_num[bigger_view.attributes_index]
    
        encode_records = np.matmul(bigger_view.tuple_key, encode_num)
    
        for i in range(self.num_key):
            key_index = np.where(encode_records == i)[0]
            self.count[i] = np.sum(bigger_view.count[key_index])

    ######################################## functions for consistency #######################
    ############ used in commom view #############
    def initialize_consist_parameters(self, num_target_views):
        self.summations = np.zeros([self.num_key, num_target_views])
        self.weights = np.zeros(num_target_views)
        
    def calculate_delta(self):
        target = np.matmul(self.summations, self.weights) / np.sum(self.weights)
        self.delta = - (self.summations.T - target).T * self.weights

    def project_from_bigger_view(self, bigger_view, index):
        encode_num = np.zeros(self.num_attributes, dtype=np.uint32)
        encode_num[self.attributes_index] = self.encode_num
        encode_num = encode_num[bigger_view.attributes_index]
        
        encode_records = np.matmul(bigger_view.tuple_key, encode_num)

        self.weights[index] = 1.0 / np.product(self.num_categories[np.setdiff1d(bigger_view.attributes_index, self.attributes_index)])

        for i in range(self.num_key):
            key_index = np.where(encode_records == i)[0]
            self.summations[i, index] = np.sum(bigger_view.count[key_index])

    ############### used in views to be consisted ###############
    def update_view(self, common_view, index):
        encode_num = np.zeros(self.num_attributes, dtype=np.uint32)
        encode_num[common_view.attributes_index] = common_view.encode_num
        encode_num = encode_num[self.attributes_index]
        
        encode_records = np.matmul(self.tuple_key, encode_num)

        for i in range(common_view.num_key):
            key_index = np.where(encode_records == i)[0]
            self.count[key_index] += common_view.delta[i, index]

    ######################################### non-negative functions ####################################
    def non_negativity(self):
        non_negativity = NonNegativity(self.count)
        
        self.count = non_negativity.norm_cut()


if __name__ == "__main__":
    view = View([1, 1, 0, 0], [3, 3, 0, 0])






