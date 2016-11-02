# encoding = utf-8
''' This script aims to automatically remove baseline and fit spectroscopic
data. It uses the curve_fit function from scipy.optimize module, and
provides fits for Gaussian and Lorentzian spectra lineshapes.

This is a simplied version from the ambitious AutoSpectraFit.py which
attempts to auto recognize lineshapes and numbers of peaks. It fails.
Therefore this version only has manual mode, which requires the user to
tell the script initial guesses. This version also handles better on SnR
calculation. Fit up to 4-th derivative.

The script supports comma, tab and space delimited xy files with any
number of lines of header information.
Requires numpy1.8+ and scipy0.16+
'''

import os
import re
import numpy as np
from scipy.optimize import curve_fit
from scipy.optimize import leastsq
from math import pi
from math import isinf
from scipy import interpolate

# ----------------------------------------
# ---- Class and Function Declaration ----
# ----------------------------------------

class Function:
    ''' Function class stores all sorts of function form. In spectroscopic
    context, gaussian/lorentzian function families are supported. Also,
    up to second derivative of these functions are defined to descibe the
    common spectra lineshape obtained by spectroscopic experiments.
    Coefficients are defined so as 0-derivative functions are normalized.
    The user may add more customized funtion form to it.
    '''

    # Class variable: function family name list. User may add their own.
    def __init__(self, ftype, der, peak):
        # Three attributes denote the function type, order of derivatives
        # and number of peaks.
        self.ftype = ftype
        self.der = der
        self.peak = peak

    def get_func(self):
        # get gaussian function family
        if not self.ftype:
            if self.der == 0:
                return self.gder0
            elif self.der == 1:
                return self.gder1
            elif self.der == 2:
                return self.gder2
            elif self.der == 3:
                return self.gder3
            elif self.der == 4:
                return self.gder4

        # get lorentzian function family
        if self.ftype == 1:
            if self.der == 0:
                return self.lder0
            elif self.der == 1:
                return self.lder1
            elif self.der == 2:
                return self.lder2
            elif self.der == 3:
                return self.lder3
            elif self.der == 4:
                return self.lder4

    # Gaussian family functions. Integrate[g(x; mu, sigma, A)] = A
    def gder0(self, x, *p):
        #! g = p[-1]
        g = 0
        for n in range(self.peak):
            A = p[3*n+2]
            sigma = p[3*n+1]
            mu = p[3*n]
            g += A/(np.sqrt(2*pi)*sigma)*np.exp(-(x-mu)**2/(2*sigma**2))
        return g

    def gder1(self, x, *p):
        #! g = p[-1]
        g = 0
        for n in range(self.peak):
            A = p[3*n+2]
            sigma = p[3*n+1]
            mu = p[3*n]
            g += -A*(x-mu)/(np.sqrt(2*pi)*sigma**3)*np.exp(-(x-mu)**2/(2*sigma**2))
        return g

    def gder2(self, x, *p):
        #! g = p[-1]
        g = 0
        for n in range(self.peak):
            A = p[3*n+2]
            sigma = p[3*n+1]
            mu = p[3*n]
            g += A/(np.sqrt(2*pi)*sigma**3)*(np.exp(-(x-mu)**2/(2*sigma**2))
                                             *((x-mu)**2/(sigma**2)-1))
        return g

    def gder3(self, x, *p):
        #! g = p[-1]
        g = 0
        for n in range(self.peak):
            A = p[3*n+2]
            sigma = p[3*n+1]
            mu = p[3*n]
            g += A/(np.sqrt(2*pi)*sigma**5)*(x-mu)*np.exp(
                 -(x-mu)**2/(2*sigma**2))*(3-((x-mu)/sigma)**2)
        return g

    def gder4(self, x, *p):
        #! g = p[-1]
        g = 0
        for n in range(self.peak):
            A = p[3*n+2]
            sigma = p[3*n+1]
            mu = p[3*n]
            g += A/(np.sqrt(2*pi)*sigma**5)*(3-6*((x-mu)/sigma)**2+
                 ((x-mu)/sigma)**4)*np.exp(-(x-mu)**2/(2*sigma**2))
        return g

    # Lorentzian family functions. Integrate[l(x; mu, gamma, A)] = A
    # gamma is FWHM
    def lder0(self, x, *p):
        #! l = p[-1]
        l = 0
        for n in range(self.peak):
            mu = p[3*n]
            gamma = p[3*n+1]
            A = p[3*n+2]
            l += A*gamma/(2*pi*((x-mu)**2+gamma**2/4))
        return l

    def lder1(self, x, *p):
        #! l = p[-1]
        l = 0
        for n in range(self.peak):
            mu = p[3*n]
            gamma = p[3*n+1]
            A = p[3*n+2]
            l += -A*gamma*(x-mu)/(pi*((x-mu)**2+gamma**2/4)**2)
        return l

    def lder2(self, x, *p):
        #! l = p[-1]
        l = 0
        for n in range(self.peak):
            mu = p[3*n]
            gamma = p[3*n+1]
            A = p[3*n+2]
            l += A*gamma*(-3*(x-mu)**2+gamma**2/4)/(pi*((x-mu)**2+gamma**2/4)**3)
        return l

    def lder3(self, x, *p):
        #! l = p[-1]
        l = 0
        for n in range(self.peak):
            mu = p[3*n]
            gamma = p[3*n+1]
            A = p[3*n+2]
            l += A*gamma*(x-mu)/(pi*((x-mu)**2+gamma**2/4)**4)*(
                 3*(x-mu)**2+5*gamma**2/4)
        return l

    def lder4(self, x, *p):
        #! l = p[-1]
        l = 0
        for n in range(self.peak):
            mu = p[3*n]
            gamma = p[3*n+1]
            A = p[3*n+2]
            l += A*gamma/(pi*((x-mu)**2+gamma**2/4)**5)*(
                 5*gamma**4/256-13*((x-mu)*gamma)**2/2-15*(x-mu)**4)
        return l


def base(xdata, popt, f):
    ''' Data outside 4 sigma/gamma are considered as baseline.
    Returns the baseline index.

    Arguments:
    xdata -- x data vector
    popt -- optimized parameter vector
    ftype -- lineshape function
    peak -- number of peaks

    Returns: index of xdata considered as baseline
    '''
    baseline_idx = np.ones_like(xdata, dtype=bool)
    if not f.ftype:
        win = 4
    elif f.ftype == 1:
        win = 2.5
    for k in range(f.peak):
        mu = popt[3*k]
        width = popt[3*k+1]
        current_idx = np.logical_or(xdata < mu-win*width, xdata > mu+win*width)
        baseline_idx = np.logical_and(baseline_idx, current_idx)
    if np.any(baseline_idx):
        return baseline_idx
    else:
        # if no data ouside 4sigma window, then everything is baseline
        # and will only do 0-order baseline removal
        return np.ones_like(xdata, dtype=bool)


def box_smooth(y, box_win):
    ''' Boxcar smooth routine. Accepts only vector '''
    return np.convolve(y, np.ones(box_win), 'valid')/box_win


def noise_db(x, residual, baseline_idx):
    ''' Calculate noise after baseline removal.
    The idea is to smooth out the residual.
    Firstly, a boxcar smooth is applied to get the overal wavy trend of the
    residual. Then the part falls into baseline_idx will be removed.
    Then the residual in the baseline window should
    be quite flat, only including random noise, and can be used to calculate
    the noise level of the spectrum. However, this baseline removal does
    not have scientific justification, so it should NOT be used to 'clean'
    the original spectrum!!! '''

    # 25 is a decent smooth window
    res_smooth = np.convolve(residual, np.ones(25), 'valid')/25
    res_smooth = np.append(res_smooth, np.zeros(12))
    res_smooth = np.insert(res_smooth, 1, np.zeros(12))
    newres = residual - res_smooth
    # correct for edge drift
    p = np.polyfit(x[:12], residual[:12], deg=1)
    q = np.polyfit(x[-12:], residual[-12:], deg=1)
    newres[:12] -= np.polyval(p, x[:12])
    newres[-12:] -= np.polyval(q, x[-12:])
    return np.std(newres[baseline_idx], dtype=np.float64), res_smooth


def fit_baseline(xdata, ydata, deg):
    ''' Simply fit polynomial baseline '''

    xshift = xdata - np.median(xdata)
    try:
        ppoly = np.polyfit(xshift, ydata, deg)
        baseline = np.polyval(ppoly, xshift)
        noise = np.std(ydata - baseline)
        fake_popt = np.array([0, 0, 0])
        return fake_popt, 0, noise, ppoly, 0
    except (TypeError, ValueError, RuntimeError):
        stat = 4           # error: baseline fit failed
        return [], [], 0, [], stat


def get_delm(testline):
    ''' Analyse delimiter in a line '''
    try:
        return re.search('\d+( |\t|,)+-?\d+', testline).group(1)
    except AttributeError:
        return False

def separate_dir(filelist):
    ''' separate file name and directory name '''
    dir_list = []
    clean_file_list = []
    for filename in filelist:
        result = re.match('(.*)/(.*)$', filename).groups()
        dir_list.append(result[0])
        clean_file_list.append(result[1])
    return dir_list, clean_file_list

def out_name_gen(in_name, replace=False):
    ''' Generate output file name from input file name '''
    # Pick out the file name before extension
    if replace:
        return re.match('([^^]*).\D{3}$', in_name).group(1)
    else:
        return 'Fit'+re.match('([^^]*).\D{3}$', in_name).group(1)


def read_file(file_name, boxwin=1, rescale=1):
    ''' Load spectrum data '''
    hd = 0
    try:        # Try to open the file
        with open(file_name, 'r') as testfile:
            testline = testfile.readline()
            while not get_delm(testline):
                testline = testfile.readline()
                hd += 1
        try:
            delm = get_delm(testline)
        except AttributeError:
            fit_stat = 3   # error: unsupported file format
            return [], [], fit_stat
    except OSError:
        fit_stat = 2       # error: file not found
        return [], [], fit_stat
    except UnicodeDecodeError:
        fit_stat = 3       # error: unsupported file format
        return [], [], fit_stat

    try:        # Try to load the file
        if delm == ' ':
            spectrum = np.loadtxt(file_name, skiprows=hd)
        else:
            spectrum = np.loadtxt(file_name, delimiter=delm, skiprows=hd)
    except ValueError:
        fit_stat = 3       # error: unsupported file format
        return [], [], fit_stat

    xdata = spectrum[:,0]
    ydata = spectrum[:,1]
    fit_stat = 0

    # perform optional boxcar smooth and rescale
    if rescale != 1:
        ydata = ydata * rescale
    if boxwin > 1:
        ydata = box_smooth(ydata, boxwin)
        xdata = xdata[boxwin/2:-boxwin/2]

    return xdata, ydata, fit_stat


def save_fit(out_name, out_tbl, popt, ftype, der, peak):
    ''' Save spectrum to csv file. If more than one peak is fitted,
    each component of these peaks are also saved.

    Arguments:
    out_name -- data file name to be saved. Automatically add .csv extension
    xdata -- x data vector
    ydata -- y data vector
    f -- fitted function
    popt -- optimized parameter vector
    fit -- fitted function data array
    baseline -- polynomial baseline vector
    '''
    out_header = 'freq,inten,fit,baseline'     # Put header information

    if peak > 1:
        # If more than one peak, also try to save individual components
        # Get the individual function form of f
        f_idv = Function(ftype, der, 1)
        # Calculate individual components
        xdata = out_tbl[:,0]
        for k in range(peak):
            popt_idv = popt[3*k:3*(k+1)]
            fit_idv = f_idv.get_func()(xdata, *popt_idv)
            # Add individual components to the end of output table
            out_tbl = np.column_stack((out_tbl, fit_idv))
            # Add component number to the header
            out_header += ',comp{:d}'.format(k+1)

    np.savetxt(out_name, out_tbl, delimiter=',',
               fmt='%.8g', header=out_header, comments='')
    return None


def save_log(out_name, popt, uncertainty, ppoly, ftype, der, peak, parname):
    ''' Save fitted parameters to log file.

    Arguments:
    out_name -- log file name to be saved. Automatically add .log extension
    f -- fitted function
    popt -- optimized parameter vector
    uncertainty -- parameter uncertainty
    snr_max -- maximum SnR of the data
    '''
    # Prepare parameter names
    if not ftype:
        ftype_str = 'Gaussian'
    elif ftype == 1:
        ftype_str = 'Lorentzian'

    # Prepare baseline function
    baseline_str = 'baseline = '
    deg = len(ppoly)-1
    for k in range(deg):
        baseline_str += '{0:+.6g}x^{1:d} '.format(ppoly[k], deg-k)
    baseline_str += '{:+.6g}\n'.format(ppoly[-1])
    #baseline_str += ' + spline\n'

    # Write info to log file
    with open(out_name, 'w', newline='') as outlog:
        outlog.write('{0:s} {1:d} derivative fit\n'.format(ftype_str, der))
        if not peak:    # if 0 peak
            outlog.write('------ No peak -----\n')
        else:
            for k in range(0, peak):
                outlog.write('------ Parameters Set {0:d}------\n'.format(k+1))
                for n in range(0,3):
                    outlog.write('{0:10s}{1:.6f} ({2:.6f})\n'.format(
                                 parname[n], popt[n+3*k], uncertainty[n+3*k]))
        outlog.write('------------------------------\n\n')
        outlog.write(baseline_str)
    return None


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>
# >>>>>>>>>> fit routine functions >>>>>>>>>>
# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

def fit_spectrum(f, xdata, ydata, init, deg, smooth_edge=False, THRESHOLD=1e-2):
    ''' spectral fitting routine.

    Arguments:
    f -- fitted function
    xdata -- x data vector
    ydata -- y data vector
    init -- parameter initial guess vector
    fit_stat -- tracker of fit status

    Keyword Arguments:
    deg -- orders of polynomial for the baseline fit. Default is 0
    THRESHOLD -- converge threshold

    Returns:
    popt -- optimized parameter vector
    uncertainty -- parameter uncertainty
    noise -- noise level
    ppoly -- coefficient vector of baseline polynomial
    fit_stat -- tracker of fit status
    '''

    # This routine applies an idea slightly different that its previous
    # AutoSpectraFit.py version

    # The spectrum contains a line-profile function, plus baseline.
    # The baseline may be wavy, and the line-profile function may also
    # not be able to fit it completely, and produce a sudo-spectral-looking
    # baseline. So the baseline fitting will also try to apply the same
    # line-profile function again.

    baseline_idx = base(xdata, init, f)
    diff = 1

    while diff > THRESHOLD:
        residual = ydata - f.get_func()(xdata, *init)
        try:
            ppoly = np.polyfit(xdata[baseline_idx] - np.median(xdata),
                               residual[baseline_idx], deg)
        except (TypeError, ValueError, RuntimeError):
            stat = 4           # error: baseline fit failed
            return [], [], 0, [], stat

        # Construct polynomial baseline removed ydata
        ydata_db = ydata - np.polyval(ppoly, xdata - np.median(xdata))

        # Let's fit curve
        try:
            popt, pcov = curve_fit(f.get_func(), xdata, ydata_db, init)
        except (TypeError, ValueError, RuntimeError):
            stat = 1                   # error_1: fit failed
            return [], [], 0, [], fit_stat

        # update residual and initial vector
        residual = ydata_db - f.get_func()(xdata, *popt)
        if smooth_edge:
            # remove additional baseline from the smoothed edge
            # and get noise estimation
            noise, baseline = noise_db(xdata, residual, baseline_idx)
        else:
            noise = np.std(residual, dtype=np.float64)
        # difference from previous fit
        diff = np.linalg.norm(popt - init)
        init = popt

    # catch the case when fit fails and pcov is infinity
    if np.any(np.isinf(pcov)):
        uncertainty = []
        stat = 1       # fit failed
    else:
        uncertainty = np.sqrt(np.diag(pcov))
        stat = 0       # fit successful

    return popt, uncertainty, noise, ppoly, stat
