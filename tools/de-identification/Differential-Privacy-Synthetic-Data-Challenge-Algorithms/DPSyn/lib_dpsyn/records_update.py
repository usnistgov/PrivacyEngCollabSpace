import logging
import copy

import numpy as np

import utility


class RecordUpdate:
    def __init__(self, num_categories, original_num_categories):
        self.logger = logging.getLogger("record_update")
        
        self.num_categories = num_categories
        self.original_num_categories = original_num_categories
    
    def initialize_records(self, num_records, num_attributes, num_views, max_iteration):
        self.records = np.empty([num_records, num_attributes], dtype=np.uint32)
        
        for j in range(num_attributes):
            if self.num_categories[j] != 0:
                self.records[:, j] = np.random.randint(0, self.num_categories[j], size=(num_records))
            else:
                self.records[:, j] = np.random.randint(0, self.original_num_categories[j], size=(num_records))
        
        self.error_tracker = np.zeros([num_views, max_iteration * 2])

    def update_records_S5(self, original_view, alpha, threshold, view_index, iteration):
        view = copy.deepcopy(original_view)
        l1_error = self.update_records_before(view, view_index, iteration)
        
        if l1_error > threshold:
            self.update_records_main(view, alpha)
            self.determine_throw_indices()
            self.handle_zero_cells(view)
            
            if iteration % 2 == 0:
                self.complete_partial_ratio(view, 0.5)
            else:
                self.complete_partial_ratio(view, 1.0)

            self.update_records_after(view, view_index, iteration)
            
            return 1
        else:
            return 0
    
    def update_records_main(self, view, alpha):
        # deal with the cell that synthesize_marginal != 0 and synthesize_marginal < actual_marginal
        self.cell_under_indices = np.where((self.synthesize_marginal < self.actual_marginal) & (self.synthesize_marginal != 0))[0]
        
        ratio_add_full = (self.actual_marginal[self.cell_under_indices] - self.synthesize_marginal[self.cell_under_indices]) \
                         / self.synthesize_marginal[self.cell_under_indices]
        self.ratio_add = np.minimum(ratio_add_full, np.full(self.cell_under_indices.shape[0], alpha))
        
        num_add = np.sum(self.ratio_add * (self.synthesize_marginal[self.cell_under_indices] * self.records.shape[0]))
        
        # deal with the case synthesize_marginal == 0 and actual_marginal != 0
        self.cell_zero_indices = np.where((self.synthesize_marginal == 0) & (self.actual_marginal != 0))[0]
        self.num_add_zero = self.actual_marginal[self.cell_zero_indices] * alpha * self.records.shape[0]
        num_add += np.sum(self.num_add_zero)
        
        # determine the number of records to be removed
        self.cell_over_indices = np.where(self.synthesize_marginal > self.actual_marginal)[0]
        beta = self.find_optimal_beta(num_add, self.cell_over_indices)
        ratio_reduce = np.minimum(
            (self.synthesize_marginal[self.cell_over_indices] - self.actual_marginal[self.cell_over_indices])
            / self.synthesize_marginal[self.cell_over_indices], np.full(self.cell_over_indices.shape[0], beta))
        self.cell_num_reduce = np.rint(ratio_reduce * (self.synthesize_marginal[self.cell_over_indices] * self.records.shape[0])).astype(int)

        self.encode_records = np.matmul(self.records[:, view.attributes_index], view.encode_num)
        self.encode_records_sort_index = np.argsort(self.encode_records)
        self.encode_records = self.encode_records[self.encode_records_sort_index]

        valid_indices = np.nonzero(self.cell_num_reduce)[0]
        self.valid_cell_over_indices = self.cell_over_indices[valid_indices]
        self.valid_cell_num_reduce = self.cell_num_reduce[valid_indices]
        self.valid_data_over_index_left = np.searchsorted(self.encode_records, self.valid_cell_over_indices, side="left")
        self.valid_data_over_index_right = np.searchsorted(self.encode_records, self.valid_cell_over_indices, side="right")
    
    def determine_throw_indices(self):
        num_reduce = np.sum(self.valid_cell_num_reduce)
        self.records_throw_indices = np.zeros(num_reduce, dtype=np.uint32)
        throw_pointer = 0

        for i, cell_index in enumerate(self.valid_cell_over_indices):
            match_records_indices = self.encode_records_sort_index[self.valid_data_over_index_left[i]: self.valid_data_over_index_right[i]]
            throw_indices = np.random.choice(match_records_indices, self.valid_cell_num_reduce[i], replace=False)
            
            self.records_throw_indices[throw_pointer: throw_pointer + throw_indices.size] = throw_indices
            throw_pointer += throw_indices.size
            
        np.random.shuffle(self.records_throw_indices)

    def complete_partial_ratio(self, view, complete_ratio):
        num_complete = np.rint((self.ratio_add * complete_ratio) * self.synthesize_marginal[self.cell_under_indices] * self.records.shape[0]).astype(int)
        num_partial = np.rint((self.ratio_add * (1 - complete_ratio)) * self.synthesize_marginal[self.cell_under_indices] * self.records.shape[0]).astype(int)
        
        valid_indices = np.nonzero(num_complete + num_partial)
        num_complete = num_complete[valid_indices]
        num_partial = num_partial[valid_indices]
        valid_cell_under_indices = self.cell_under_indices[valid_indices]
        valid_data_under_index_left = np.searchsorted(self.encode_records, valid_cell_under_indices, side="left")
        valid_data_under_index_right = np.searchsorted(self.encode_records, valid_cell_under_indices, side="right")
        
        for index, cell_index in enumerate(valid_cell_under_indices):
            match_records_indices = self.encode_records_sort_index[valid_data_under_index_left[index]: valid_data_under_index_right[index]]
        
            if self.records_throw_indices.shape[0] >= (num_complete[index] + num_partial[index]):
                # complete code
                if num_complete[index] != 0:
                    self.records[self.records_throw_indices[: num_complete[index]]] = self.records[match_records_indices[: num_complete[index]]]
            
                # partial code
                if num_partial[index] != 0:
                    for i in range(view.ways):
                        # self.records[self.records_throw_indices[num_complete[index]: (num_complete[index] + num_partial[index])],
                        #              view.attributes_index[i]] = view.tuple_key[cell_index, i]
                        self.records[np.ix_(self.records_throw_indices[num_complete[index]: (num_complete[index] + num_partial[index])],
                                            view.attributes_index)] = view.tuple_key[cell_index]
            
                self.records_throw_indices = self.records_throw_indices[num_complete[index] + num_partial[index]:]
        
            else:
                self.records[self.records_throw_indices] = self.records[match_records_indices[: self.records_throw_indices.size]]

    def handle_zero_cells(self, view):
        # overwrite / partial when synthesize_marginal == 0
        if self.cell_zero_indices.size != 0:
            for index, cell_index in enumerate(self.cell_zero_indices):
                num_partial = int(round(self.num_add_zero[index]))
            
                if num_partial != 0:
                    for i in range(view.ways):
                        self.records[self.records_throw_indices[: num_partial], view.attributes_index[i]] = \
                        view.tuple_key[cell_index, i]
            
                self.records_throw_indices = self.records_throw_indices[num_partial:]
    
    def find_optimal_beta(self, num_add, cell_over_indices):
        actual_marginal_under = self.actual_marginal[cell_over_indices]
        synthesize_marginal_under = self.synthesize_marginal[cell_over_indices]
        
        lower_bound = 0.0
        upper_bound = 1.0
        beta = 0.0
        current_num = 0.0
        
        while abs(num_add - current_num) > 10.0:
            beta = (upper_bound + lower_bound) / 2.0
            current_num = np.sum(
                np.minimum((synthesize_marginal_under - actual_marginal_under) / synthesize_marginal_under,
                           np.full(cell_over_indices.shape[0], beta)) * synthesize_marginal_under * self.records.shape[0])
            
            if current_num < num_add:
                lower_bound = beta
            elif current_num > num_add:
                upper_bound = beta
            else:
                return beta
        
        return beta
    
    def update_records_before(self, view, view_index, iteration):
        self.actual_marginal = view.normalize_count
        self.synthesize_marginal = self.synthesize_marginal_distribution(view)
        
        l1_error = utility.l1_distance(self.actual_marginal, self.synthesize_marginal)
        self.error_tracker[view_index, 2 * iteration] = l1_error
        
        self.logger.info("the l1 error before updating is %s" % (l1_error,))
        
        return l1_error
    
    def update_records_after(self, view, view_index, iteration):
        self.synthesize_marginal = self.synthesize_marginal_distribution(view)
        
        l1_error = utility.l1_distance(self.actual_marginal, self.synthesize_marginal)
        self.error_tracker[view_index, 2 * iteration + 1] = l1_error
        
        self.logger.info("the l1 error after updating is %s" % (l1_error,))

        if iteration == 1:
            np.random.shuffle(self.records)
    
    def synthesize_marginal_distribution(self, view):
        count = view.count_records_general(self.records)
        # count_matrix = view.calculate_count_matrix_general(count)
        
        return view.calculate_normalize_count_general(count)

    # based on minimum cost flow, all overwrite
    def update_records_fully(self, original_view, threshold, view_index, iteration):
        view = copy.deepcopy(original_view)
        l1_error = self.update_records_before(view, view_index, iteration)

        if l1_error > threshold:
            self.marginal_reallocation = self.determine_marginal_reallocation()
    
            # encode the synthesized records
            encode_records = np.matmul(self.records[:, view.attributes_index], view.encode_num)
    
            for key_index in range(view.num_key):
                # get the indices corresponding to each key
                key_index_list = np.where(encode_records == key_index)[0]
                nonzero_index = np.nonzero(self.marginal_reallocation[key_index])[0]
                cum_sum = np.cumsum(self.marginal_reallocation[key_index, nonzero_index])
                start = 0
        
                for index, value in enumerate(cum_sum):
                    end = int(round(key_index_list.shape[0] * value))
            
                    indices = key_index_list[start: end]
                    start = end
            
                    for i in range(view.ways):
                        self.records[indices, view.attributes_index[i]] = view.tuple_key[nonzero_index[index], i]
    
            self.update_records_after(view, view_index, iteration)
    
            return 1
        else:
            return 0

    def determine_marginal_reallocation(self):
        marginal_reallocation = self.minimum_cost_flow_problem_intuitive()

        summation = np.sum(marginal_reallocation, axis=1)

        nonzero_index = np.nonzero(summation)[0]

        marginal_reallocation[nonzero_index] = (marginal_reallocation[nonzero_index].T / summation[nonzero_index]).T

        return marginal_reallocation

    def minimum_cost_flow_problem_intuitive(self):
        actual_distribution = copy.deepcopy(self.actual_marginal)
        synthesize_distribution = copy.deepcopy(self.synthesize_marginal)

        num_cells = len(actual_distribution)
        marginal_reallocation = np.zeros([num_cells, num_cells])

        minimum_value = np.minimum(actual_distribution, synthesize_distribution)

        actual_distribution -= minimum_value
        synthesize_distribution -= minimum_value

        self.actual_cumulative(marginal_reallocation, actual_distribution, synthesize_distribution)

        marginal_reallocation[[i for i in range(num_cells)], [j for j in range(num_cells)]] = minimum_value

        return marginal_reallocation

    def actual_cumulative(self, marginal_reallocation, actual_distribution, synthesize_distribution):
        while (not np.sum(synthesize_distribution) == 0) and (not np.sum(actual_distribution) == 0):
            nonzero_index = np.nonzero(synthesize_distribution)[0][0]
            nonzero_value = synthesize_distribution[nonzero_index]
    
            actual_cum_sum = np.cumsum(actual_distribution)
            result_index = np.nonzero((actual_cum_sum <= nonzero_value) & (actual_cum_sum > 0.0))[0]
            try:
                next_index = np.nonzero(actual_cum_sum > nonzero_value)[0][0]
            except:
                next_index = np.nonzero((actual_cum_sum <= nonzero_value) & (actual_cum_sum > 0.0))[0][0]
    
            if result_index.size == 0:
                marginal_reallocation[nonzero_index, next_index] = nonzero_value
                synthesize_distribution[nonzero_index] = 0.0
                actual_distribution[next_index] -= nonzero_value
            else:
                marginal_reallocation[nonzero_index, result_index] = actual_distribution[result_index]
                synthesize_distribution[nonzero_index] -= np.sum(actual_distribution[result_index])
                actual_distribution[result_index] = 0.0
        
                if result_index[-1] > next_index:
                    synthesize_distribution[nonzero_index] = 0.0
                elif actual_cum_sum[result_index[-1]] < nonzero_value:
                    marginal_reallocation[nonzero_index, next_index] = nonzero_value - actual_cum_sum[
                        result_index[-1]]
                    synthesize_distribution[nonzero_index] = 0.0
                    actual_distribution[next_index] = actual_cum_sum[next_index] - nonzero_value


if __name__ == "__main__":
    update = RecordUpdate(None)
    
    update.synthesize_marginal = np.array([0.4, 0.6])
    update.actual_marginal = np.array([0.6, 0.4])