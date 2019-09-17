import numpy as np


class NonNegativity:
    def __init__(self, count):
        self.count = np.copy(count)
    
    def norm_cut(self):
        # set all negative value to 0.0
        negative_indices = np.where(self.count < 0.0)[0]
        negative_total = abs(np.sum(self.count[negative_indices]))
        self.count[negative_indices] = 0.0
        
        # find all positive value and sort them in ascending order
        positive_indices = np.where(self.count > 0.0)[0]
        
        if positive_indices.size != 0:
            positive_sort_indices = np.argsort(self.count[positive_indices])
            sort_cumsum = np.cumsum(self.count[positive_indices[positive_sort_indices]])
            
            # set the smallest positive value to 0.0 to preserve the total density
            threshold_indices = np.where(sort_cumsum <= negative_total)[0]
            
            if threshold_indices.size == 0:
                self.count[positive_indices[positive_sort_indices[0]]] = sort_cumsum[0] - negative_total
            else:
                self.count[positive_indices[positive_sort_indices[threshold_indices]]] = 0.0
                next_index = threshold_indices[-1] + 1
                
                # self.count[positive_indices[positive_sort_indices[next_index]]] = sort_cumsum[next_index] - negative_total
                
                if next_index < positive_sort_indices.size:
                    self.count[positive_indices[positive_sort_indices[next_index]]] = sort_cumsum[next_index] - negative_total
                # else:
                #     self.count[positive_indices[positive_sort_indices[-1]]] = sort_cumsum[-1] - negative_total
        else:
            self.count[:] = 0.0
        
        return self.count
