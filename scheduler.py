import numpy as np

def softmax(z):
    z = z - np.max(z)
    e = np.exp(z)
    return e / e.sum()

class HopAwareScheduler:
    """Mirror‑descent + hop penalty (simplified). Works identically on every node."""
    def __init__(self, F:int, H:np.ndarray, mu:int=10, gamma0:float=1.0):
        self.F = F
        self.H = H              # P×(F+1) incidence on infeasible flows
        self.P = H.shape[0]
        self.mu = mu
        self.gamma = gamma0
        self.pq = np.full(F+1, 1.0/(F+1))
        self.lamdual = np.zeros(self.P)
        self.t = 0
        # conservative bounds
        self.G_U = mu
        self.G_phi = 2*np.max(np.linalg.norm(H, axis=1))
    def step(self, lam_vec):
        """One MD + dual ascent step; lam_vec is offered load per class (length F)."""
        self.t += 1
        eta = (self.G_U + self.gamma*self.G_phi)**-1 * np.sqrt(np.log(self.F+1)/(self.t))
        # gradient of U
        grad_U = np.zeros(self.F+1)
        for f in range(1,self.F+1):
            grad_U[f] = self.mu if self.pq[f]*self.mu < lam_vec[f-1] else 0.0
        # gradient of phi
        grad_phi = 2 * self.H.T @ (self.H @ self.pq)
        g = -grad_U + self.H.T @ self.lamdual + self.gamma*grad_phi
        self.pq = softmax(np.log(self.pq+1e-20) - eta*g)
        self.lamdual = np.maximum(0.0, self.lamdual + eta*(self.H @ self.pq))
        return self.pq.copy()
