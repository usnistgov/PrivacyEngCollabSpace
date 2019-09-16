import numpy as np
from scipy.sparse.linalg import LinearOperator

class Identity(LinearOperator):
    def __init__(self, n, dtype=np.float64):
        self.shape = (n,n)
        self.dtype = dtype

    def _matmat(self, V):
        return V

    def _transpose(self):
        return self

    def _adjoint(self):
        return self

