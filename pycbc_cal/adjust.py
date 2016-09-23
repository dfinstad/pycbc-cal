import matplotlib.pyplot as plt
import numpy as np
import pycbc
import scipy

# set FFTW measure level to 0 so that time isn't wasted doing planning
from pycbc.fft.fftw import set_measure_level
set_measure_level(0)

def adjust_strain_with_new_transfer_function(strain, cal, deltafc=0.0, kc=1.0, ktst=1.0, kpu=1.0, ktstim=0.0, kpuim=0.0, plots=None):
    """Adjust the TimeSeries strain by changing the time-dependent calibration parameters
    kappa_C(t), kappa_A(t), and \Delta f_c(t) = f_c(t) - f_c(t_0).
    
    Parameters
    ----------
    strain : TimeSeries
        The strain, darm_error, etc. that you want to adjust.
    cal : Calibration object
        Calibration data for the detector.
    deltafc : float
        Change in coupled-cavity (CC) pole at a time t: \Delta f_c(t) = f_c(t) - f_c(t_0)
    kc : float
        Scalar correction factor for sensing function C0 at time t
    ktst : float
        Real part of scalar correction factor for actuation function Atst0 at time t
    kpu : float
        Real part of scalar correction factor for actuation function Apu0 at time t
    ktstim : float
        Imaginary part of scalar correction factor for actuation function Atst0 at time t
    kpuim : float
        Imaginary part of scalar correction factor for actuation function Apu0 at time t
    plots : bool
        Make plots.
    
    Returns
    -------
    strain_adjusted : TimeSeries
        The adjusted strain
    """

    ############### Convert strain TimeSeries to FrequencySeries ##############
    strain_tilde = strain.to_frequencyseries()

    ############### Calculate the tranfer function error K(f) FrequencySeries #############

    # Get the 'true' and 'adjusted' transfer functions
    Rtrue = cal.R0
    Radjusted = cal.update_R(deltafc=deltafc, kc=kc, ktst=ktst, kpu=kpu, ktstim=ktstim, kpuim=kpuim)

    # Get the error function to apply to the strain in the frequency-domain
    K = Radjusted/Rtrue

    # Decompose into amplitude and unwrapped phase
    Kamp = np.abs(K)
    Kphase = np.unwrap(np.angle(K))

    # Convert to a FrequencySeries by interpolating then resampling
    order = 1
    Kampoff = scipy.interpolate.UnivariateSpline(cal.freq, Kamp, k=order, s=0)
    Kphaseoff = scipy.interpolate.UnivariateSpline(cal.freq, Kphase, k=order, s=0)
    # Interpolation/vector operations are much faster if you convert FrequencySeries things to numpy arrays
    freq_even = strain_tilde.sample_frequencies.numpy()
    K_even_sample = Kampoff(freq_even)*np.exp(1.0j*Kphaseoff(freq_even))
    strain_tilde_adjusted = pycbc.types.FrequencySeries(strain_tilde.numpy()*K_even_sample, delta_f=strain_tilde.delta_f)

    ################### Convert back to TimeSeries ###################
    strain_adjusted = strain_tilde_adjusted.to_timeseries()
    # You have to manually set the start time again
    strain_adjusted.start_time = strain.start_time

    ################# make plots ################
    if plots:
        di = 10000

        # Make the amplitude error plot
        fig = plt.figure(figsize=(16, 8))
        axes = fig.add_subplot(211)
        axes.semilogx(freq_even[::di], np.abs(K_even_sample[::di]), ls='-', lw=2)
        axes.hlines(1.0, cal.freq[0], cal.freq[-1], linestyles=':')
        axes.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes.set_ylabel(r'$|K|$', fontsize=16)
        # Make the phase error plot
        axes = fig.add_subplot(212)
        axes.semilogx(freq_even[::di], np.unwrap(np.angle(K_even_sample[::di])), ls='-', lw=2)
        axes.hlines(0.0, cal.freq[0], cal.freq[-1], linestyles=':')
        axes.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes.set_ylabel(r'phase$(K)$', fontsize=16)

        fig = plt.figure(figsize=(16, 3))
        axes = fig.add_subplot(111)
        axes.loglog(strain_tilde.sample_frequencies.numpy()[::di], np.abs(strain_tilde.numpy()[::di]), ls='-', lw=2, label='true')
        axes.loglog(strain_tilde_adjusted.sample_frequencies.numpy()[::di], np.abs(strain_tilde_adjusted.numpy()[::di]), ls='-', lw=2, label='adjusted')
        axes.set_xlim([8.0, 10000.0])
        #axes.set_ylim([1e-24, 1e-22])
        axes.set_xlabel(r'$f$ (Hz)', fontsize=16)
        axes.set_ylabel(r'$|\tilde d|$', fontsize=16)
        axes.set_xticklabels(axes.get_xticks(), fontsize=14)
        axes.set_yticklabels(axes.get_yticks(), fontsize=14)
        axes.minorticks_on()
        axes.tick_params(which='major', width=2, length=8)
        axes.tick_params(which='minor', width=2, length=4)
        axes.legend(loc='best')

        fig = plt.figure(figsize=(16, 3))
        axes = fig.add_subplot(1, 1, 1)
        axes.plot(strain.sample_times.numpy()[::di], strain.numpy()[::di], ls='-', label='true')
        axes.plot(strain_adjusted.sample_times.numpy()[::di], strain_adjusted.numpy()[::di], ls='-', label='adjusted')
        axes.legend(loc='best')


    return strain_adjusted
