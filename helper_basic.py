
# Python standard library
import inspect
import os, sys
import importlib
from importlib import reload

# Other libraries
import scipy
import scipy.optimize
import numpy as np

from pylab import *


    
def Uniform(x,A):
    if type(x) not in [np.ndarray,list]:
        return A
    else:
        return A*np.ones_like(x)
def Exp(x,A,t):
    return A*np.exp(-x/t)
def Gauss(x, A, mean, sigma):
    return A * np.exp(-(x - mean)**2 / (2 * sigma**2)) 
def Gauss_sideband(x, A, mean, sigma, a1,a2):
    # a1 for left, a2 for right
    return Utils.Gauss(x, A, mean, sigma) + sqrt(2*np.pi)*sigma/2*(a1*scipy.special.erfc((x-mean)/sqrt(2)/sigma) + a2*(2-scipy.special.erfc((x-mean)/sqrt(2)/sigma))) 
def Poisson(k, Lambda,A):
    # Lambda: mean, A: amplitude
    return A*(Lambda**k/scipy.special.factorial(k)) * np.exp(-Lambda)
def Poly(x, *P):
    '''
    Compute polynomial P(x) where P is a vector of coefficients
    Lowest order coefficient at P[0].  Uses Horner's Method.
    '''
    result = 0
    for coeff in P[::-1]:
        result = x * result + coeff
    return result
def Chi2(x, dof, A):
    return scipy.stats.chi2.pdf(x,dof)*A  

def fit_curve(f, xdata, ydata, p0=None, sigma=None, absolute_sigma=False, check_finite=None, bounds=(-np.inf, np.inf), method=None, jac=None, **kwargs):
   
    if type(f) is str:
        if f in ["Gauss","gauss","gaus"]:
            f=Gauss
            mean = np.sum(xdata*ydata)/np.sum(ydata)
            p0 = [np.max(ydata), mean, np.sqrt(np.sum(ydata*(xdata-mean)**2)/(np.sum(ydata)-1))] if p0 is None else p0
            sigma = np.sqrt(ydata) if sigma is None else sigma; sigma[sigma==0] =1
        elif f in ["Exp", "exp"]:
            f=Exp
            
            
    popt, pcov, info, *_ = scipy.optimize.curve_fit(f, xdata, ydata, p0=p0, sigma=sigma, absolute_sigma=absolute_sigma, check_finite=check_finite, bounds=bounds, method=method, jac=jac, full_output=True, **kwargs)   
    
    return popt, pcov, info, f
    
    
def fit_hist(f, h, makeplot = True, label=None, fit_range=None, p0=None, sigma=None, absolute_sigma=False, check_finite=None, bounds=(-np.inf, np.inf), method=None, jac=None, full_output=False, nan_policy=None, **kwargs):
    def fstr(template, scope):
        return eval(f"f'{template}'", scope)    
    
    xdata = 0.5*(h[1][:-1]+h[1][1:])
    ydata = h[0]
    fit_range = [xdata[0], xdata[-1]] if fit_range is None else fit_range
    mask = (xdata>=fit_range[0]) &(xdata<=fit_range[1])
    xdata = xdata[mask]
    ydata = ydata[mask]
    
    popt, pcov, info, f = fit_curve(f, xdata, ydata, p0=p0, sigma=sigma, absolute_sigma=absolute_sigma, check_finite=check_finite, bounds=bounds, method=method, jac=jac, **kwargs)

    if makeplot:
        xdata_plot = np.linspace(*fit_range, 200)
        ydata_plot = f(xdata_plot, *popt)
        
        scope = locals()
        func_parameter_names = inspect.getfullargspec(f)[0][1:]
        label = fstr(label,scope) if label is not None else "Fit"
        plot(xdata_plot, ydata_plot, label=label)
    
    return popt, pcov, info, f