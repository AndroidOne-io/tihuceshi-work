# ζ(s) 的 Borwein 算法（不依赖 mpmath），用于临界线曲线
import numpy as np
def _dk(n):
    term, terms = 1.0, [1.0]
    for i in range(n):
        term *= (n + i) * 4.0 * (n - i) / ((2 * i + 1) * (2 * i + 2)); terms.append(term)
    return np.cumsum(terms)            # d_0..d_n
def zeta(s, n=110):
    s = np.asarray(s, complex); d = _dk(n); k = np.arange(n)
    coef = ((-1.0) ** k) * (d[:n] - d[n])
    tot = (coef[None, :] * np.exp(-s[..., None] * np.log(k + 1.0)[None, :])).sum(-1)
    return -tot / (d[n] * (1 - 2.0 ** (1 - s)))
if __name__ == '__main__':
    for t in (14.134725, 21.022040, 25.010858, 0.0, 10.0):
        print(t, abs(zeta(0.5 + 1j * t)), zeta(0.5 + 1j * t))
