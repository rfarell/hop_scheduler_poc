import numpy as np

def poisson_arrivals(lam_vec):
    """Return list of arrivals counts per class (len F)."""
    return np.random.poisson(lam_vec)
