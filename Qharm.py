import numpy as np
import math

class Experiment:
    m = 1.0 # double
    w = 1.0
    a = 1.0
    s = 1.0
    kappa = 1.0 
    n = 13 # int
    h = 1 
    random = False
    coherent = True
    squeezed = False

    def Psi(self, x, T):
        self.kappa = math.sqrt(self.m * self.w / self.h)
        
        c = self.coeff(x, T)

        psi = Herm_sum_m(c, self.n - 1, self.kappa * x)
    
        return psi

    def coeff(self, x, t):
        c = np.zeros(self.n, dtype=complex)
        for m in range (0, self.n):
            c[m] = (self.w_m(m) * self.N_m(m) * self.Phi_m(x)) * \
                    Exp_i_phi(-self.E_m(m) * t) 
        return c

    def w_m(self, m):
        s = self.s
        a = self.a
        if self.random:
            return self.data[m]
        if (self.coherent) or (s < 1.01):
            return math.pow(a, m) * math.exp(-a * a / 2) \
                 / math.sqrt(fact(m))
        if (self.squeezed) or (s > 1.01):
            return math.sqrt(2*math.sqrt(s)/(s+1)) * \
                   math.pow(((s-1)/(s+1)), m/2) * \
                   (1 / math.sqrt(math.pow(2, m) * fact(m))) * \
                   Herm_m(m, (s*math.sqrt(2)*a/math.sqrt(s*s-1))) * \
                   math.exp(-s*a*a/(s+1)) 
        else:
            return 0

    def E_m(self, m):
        w = self.w
        return 0.5 * w * (2 * m + 1) # En/h, En = hw/2 * (2n+1)

    def N_m(self, m):
        # (kappa^2/pi)^(1/4) * 1/sqrt(2^m * m!)
        kappa = self.kappa
        return math.pow((kappa * kappa / math.pi), 0.25) \
            / (math.sqrt(math.pow(2, m) * fact(m))) 

    def Phi_m(self, x):
        # exp ( - (kappa*x)^2 / 2)
        kappa = self.kappa
        return math.exp(- math.pow(kappa * x, 2) / 2)           

# special functions
def Exp_i_phi(phi):
    real = math.cos(phi) # exp(i*phi).x
    imag = math.sin(phi) # exp(i*phi).y
    return complex(real, imag)

def fact(m):
    res = 1
    for i in range (1,  m):
        res *= i
    return res

def Herm_sum_m(c, n, x):
    # Clenshaw's method
    res = complex(0)
    b1 = complex(0)
    b2 = complex(0)
    i = complex(0)

    for i in range(n, -1, -1):
        res = 2 * (x * b1 - (i + 1) * b2) + c[i]
        b2 = b1
        b1 = res
    return res

def Herm_m(m, x):
    res = 0
    a = 1
    b = 2*x
    
    if (m == 0):
        res = a
        return res
    if (m == 1):
        res = b
        return res
    for i in range(2, m):
        res = 2*x*b-2*(i-1)*a
        a = b
        b = res
    return res

def norm(psi):
    return psi.real*psi.real + psi.imag*psi.imag
