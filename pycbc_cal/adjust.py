import matplotlib.pyplot as plt
import numpy as np
import pycbc
import scipy

# set FFTW measure level to 0 so that time isn"t wasted doing planning
from pycbc.fft.fftw import set_measure_level
set_measure_level(0)

def adjust_strain(strain, cal, deltafc=0.0, kc=1.0, ktst=1.0, kpu=1.0):
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
        Scalar correction factor for actuation function Atst0 at time t
    kpu : float
        Scalar correction factor for actuation function Apu0 at time t
    
    Returns
    -------
    strain_adjusted : TimeSeries
        The adjusted strain
    """

    # Fourier transform
    strain_tilde = strain.to_frequencyseries()

    # Get the "true" and "adjusted" transfer functions
    Rtrue = cal.R0
    Radjusted = cal.update_R(deltafc=deltafc, kc=kc, ktst=ktst, kpu=kpu)

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

    return strain_adjusted
