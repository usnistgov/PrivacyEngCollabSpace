import numpy as np


class AdvancedComposition:
    def __init__(self):
        pass

    def my_minimize(self, func, l, h):
        vfunc = np.vectorize(func)
        cur_l, cur_h = l, h
        n = 20000
        for i in range(10):
            xs = np.linspace(cur_l, cur_h, n)
            vs = vfunc(xs)
            vs_index = np.argsort(vs)
            cur_l_index, cur_h_index = vs_index[0], vs_index[1]
            cur_l, cur_h = xs[cur_l_index], xs[cur_h_index]
    
        return (cur_l + cur_h) / 2

    def gauss_renyi(self, epsilon, delta, sensitivity, k):
        def renyi(low):
            epsilon0 = max(1e-20, epsilon - np.log(1.0 / delta) * 1.0 / (low - 1))
            sigma = np.sqrt(k * low * sensitivity * 1.0 / 2 / epsilon0)
            return sigma
    
        l, h = 1.00001, 100000
        min_low = self.my_minimize(renyi, l, h)
        min_sigma = renyi(min_low)
    
        return min_sigma
