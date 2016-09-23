import matplotlib.pyplot as plt
import matplotlib.ticker as tick
import numpy as np
#import scipy.interpolate

# TimeSeries, FrequencySeries
#import pycbc
#from pycbc import types
#import pycbc.types

# set FFTW measure level to 0 so that time isn't wasted doing planning
#from pycbc.fft.fftw import set_measure_level
#set_measure_level(0)

def amp_to_dB(x):
    """Calculate the amplitude of the quantity x (could be complex) in decibels.
    """
    return 20.0*np.log10(np.abs(x))


def dB_to_amp(dB):
    """Convert decibels to amplitude.
    """
    return 10**(dB/20.0)


def zpk_file_to_array(filename):
    """Convert the contents of a zpk file with the columns [freq, real(H), imag(H)]
    to an array with columns [freq, real(H)+j*imag(H)].
    """
    data = np.loadtxt(filename)
    freq = data[:, 0]
    H = data[:, 1]+1.0j*data[:, 2]
    
    return np.array([freq, H]).T


def transfer_function_error(Rtrue, Rmeasured):
    """Calculate the response function error K(f) = R_{measured}(f)/R_{true}(f) = (1+\delta A/A)e^{i\delta\phi}.
    Also calculate \delta A/A and \delta\phi.
    """
    
    K = Rmeasured/Rtrue
    dAbyA = np.abs(K)-1.0
    dphi = np.angle(K)
    return K, dAbyA, dphi


###################### Plots ###############################

def bode_plot(frequency_list, data_list, dB=False, degrees=False, unwrap=False, ylabel=None, labels=None):
    """Make a Bode plot (amplitude and phase as a function of frequency).
    
    Parameters
    ----------
    frequency_list : list of arrays
    data_list : list of complex arrays
    db : bool
        Plot the amplitude in decibels.
    degrees : bool
        Plot the phase in degrees (radians by default).
    unwrap : bool
        Unwrap the phase.
    """
    
    fig = plt.figure(figsize=(16, 6))
    axes1 = fig.add_subplot(121)
    axes2 = fig.add_subplot(122)
    
    for i in range(len(data_list)):
        freq = frequency_list[i]
        # Calculate amplitude and phase
        amplitude = np.abs(data_list[i])
        phase = np.angle(data_list[i])
        # Unwrap phase and convert from radians to degrees if desired
        if unwrap:
            phase = np.unwrap(phase)
        if degrees:
            phase = phase * 180.0/np.pi
        # Get legend label
        if labels:
            label=labels[i]
        else:
            label=str(i)
            
        # Make the amplitude plot
        if dB:
            dB_rescale = amp_to_dB(amplitude)
            axes1.semilogx(freq, dB_rescale, ls='-', lw=2, label=label)
        else:
            axes1.loglog(freq, amplitude, ls='-', lw=2, label=label)
            axes1.yaxis.set_major_formatter(tick.FormatStrFormatter('%2.2e'))
            #axes1.get_yaxis().get_major_formatter().set_scientific(True)
        axes1.set_xlabel(r'$f$ (Hz)', fontsize=16)
        if ylabel: axes1.set_ylabel(ylabel, fontsize=16)
        axes1.set_xticklabels(axes1.get_xticks(), fontsize=14)
        axes1.set_yticklabels(axes1.get_yticks(), fontsize=14)
        axes1.minorticks_on()
        axes1.tick_params(which='major', width=2, length=8)
        axes1.tick_params(which='minor', width=2, length=4)
        axes1.grid(True, which='major', ls="-", color='k')
        #axes1.legend(loc='upper right')
        axes1.legend(loc='best')
        
        # Make the phase plot
        axes2.semilogx(freq, phase, ls='-', lw=2, label=label)
        axes2.set_xlabel(r'$f$ (Hz)', fontsize=16)
        if degrees:
            axes2.set_ylabel('Phase (degrees)', fontsize=16)
            pmin = np.floor(min(phase)/180.0)*180.0
            pmax = np.ceil(max(phase)/180.0)*180.0
            for p in np.arange(pmin, pmax, 180.0):
                axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
        else:
            axes2.set_ylabel('Phase (radians)', fontsize=16)
            pmin = np.floor(min(phase)/np.pi)*np.pi
            pmax = np.ceil(max(phase)/np.pi)*np.pi
            for p in np.arange(pmin, pmax, np.pi):
                axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
        
        axes2.xaxis.grid(True, which="major", ls="-", color='k')
        axes2.set_xticklabels(axes2.get_xticks(), fontsize=14)
        axes2.set_yticklabels(axes2.get_yticks(), fontsize=14)
        axes2.minorticks_on()
        axes2.tick_params(which='major', width=2, length=8)
        axes2.tick_params(which='minor', width=2, length=4)
        #axes2.legend(loc='upper right')
        axes2.legend(loc='best')


def transfer_function_error_plot(frequency_list, Rtrue_list, Rmeasured_list, degrees=False, unwrap=False, labels=None):
    """Plot the fractional amplitude error and the absolute phase error for a list of transfer functions.
    
    Parameters
    ----------
    frequency_list : list of arrays
    Rtrue_list : list of complex arrays
        The true transfer functions.
    Rmeasured_list : list of complex arrays
        The measured transfer functions.
    degrees : bool
        Plot the phase in degrees (radians by default).
    unwrap : bool
        Unwrap the phase.
    """
    
    fig = plt.figure(figsize=(16, 6))
    axes1 = fig.add_subplot(121)
    axes2 = fig.add_subplot(122)
    
    for i in range(len(frequency_list)):
        freq = frequency_list[i]
        Rtrue = Rtrue_list[i]
        Rmeasured = Rmeasured_list[i]
        K, dAbyA, dphi = transfer_function_error(Rtrue, Rmeasured)
        # Unwrap phase and convert from radians to degrees if desired
        if unwrap:
            dphi = np.unwrap(dphi)
        if degrees:
            dphi = dphi * 180.0/np.pi
        # Get legend label
        if labels:
            label=labels[i]
        else:
            label=str(i)
            
        # Make the amplitude error plot
        axes1.semilogx(freq, dAbyA, ls='-', lw=2, label=label)
        axes1.hlines(0.0, freq[0], freq[-1], linestyles=':')
        axes1.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes1.set_ylabel(r'$\delta A/A$', fontsize=16)
        axes1.set_xticklabels(axes1.get_xticks(), fontsize=14)
        axes1.set_yticklabels(axes1.get_yticks(), fontsize=14)
        axes1.minorticks_on()
        axes1.tick_params(which='major', width=2, length=8)
        axes1.tick_params(which='minor', width=2, length=4)
        #axes1.legend(loc='upper right')
        axes1.legend(loc='best')
        
        # Make the phase plot
        axes2.semilogx(freq, dphi, ls='-', lw=2, label=label)
        axes2.set_xlabel(r'$f$ (Hz)', fontsize=16)
        if degrees:
            axes2.set_ylabel(r'$\delta\phi$ (degrees)', fontsize=16)
            #pmin = np.floor(min(dphi)/180.0)*180.0
            #pmax = np.ceil(max(dphi)/180.0)*180.0
            #for p in np.arange(pmin, pmax, 180.0):
            #    axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
        else:
            axes2.set_ylabel(r'$\delta\phi$ (radians)', fontsize=16)
            #pmin = np.floor(min(dphi)/np.pi)*np.pi
            #pmax = np.ceil(max(dphi)/np.pi)*np.pi
            #for p in np.arange(pmin, pmax, np.pi):
            #    axes2.hlines(p, freq[0], freq[-1], linestyles=':')
            #axes2.set_ylim(pmin, pmax)
            
        axes2.hlines(0.0, freq[0], freq[-1], linestyles=':')
        axes2.set_xticklabels(axes2.get_xticks(), fontsize=14)
        axes2.set_yticklabels(axes2.get_yticks(), fontsize=14)
        axes2.minorticks_on()
        axes2.tick_params(which='major', width=2, length=8)
        axes2.tick_params(which='minor', width=2, length=4)
        #axes2.legend(loc='upper right')
        axes2.legend(loc='best')





