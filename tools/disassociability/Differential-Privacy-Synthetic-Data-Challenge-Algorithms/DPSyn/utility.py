import numpy as np


def l1_distance(t1, t2):
    assert t1.shape[0] == t2.shape[0]
    
    return np.sum(np.absolute(t1 - t2))
