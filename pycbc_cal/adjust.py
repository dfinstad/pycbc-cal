""" Functions for adjusting the strain.
"""

import numpy
import pycbc
import scipy

def adjust_strain(strain, cal, delta_fc=0.0, kappa_c=1.0,
                  kappa_tst_re=1.0, kappa_tst_im=0.0,
                  kappa_pu_re=1.0, kappa_pu_im=0.0):
    """Adjust the TimeSeries strain by changing the time-dependent calibration
    parameters kappa_c(t), kappa_a(t), and \Delta f_c(t) = f_c(t) - f_c(t_0).
    
    Parameters
    ----------
    strain : TimeSeries
        The strain that you want to adjust.
    cal : Calibration instance
        Calibration data for the detector.
    delta_fc : float
        Change in coupled-cavity (CC) pole at a time t:
        \Delta f_c(t) = f_c(t) - f_c(t_0)
    kappa_c : float
        Scalar correction factor for sensing function c0 at time t.
    kappa_tst_re : float
        Real part of scalar correction factor for actuation function A_{tst0}
        at time t.
    kappa_tst_im : float
        Imaginary part of scalar correction factor for actuation function
        A_tst0 at time t.
    kappa_pu_re : float
        Real part of scalar correction factor for actuation function A_{pu0}
        at time t.
    kappa_pu_im : float
        Imaginary part of scalar correction factor for actuation function
        A_{pu0} at time t.
    
    Returns
    -------
    strain_adjusted : TimeSeries
        The adjusted strain.
    """

    # convert time series to frequency domain
    strain_tilde = strain.to_frequencyseries()

    # get the "true" and "adjusted" transfer functions
    r_true = cal.R0
    r_adjusted = cal.update_R(deltafc=delta_fc, kc=kappa_c,
                              ktst=kappa_tst_re,
                              ktstim=kappa_tst_im,
                              kpu=kappa_pu_re,
                              kpuim=kappa_pu_im)

    # get the error function to apply to the strain in the frequency-domain
    k = r_adjusted / r_true

    # decompose into amplitude and unwrapped phase
    k_amp = numpy.abs(k)
    k_phase = numpy.unwrap(numpy.angle(k))

    # convert to a FrequencySeries by interpolating then resampling
    order = 1
    k_amp_off = scipy.interpolate.UnivariateSpline(cal.freq, k_amp,
                                                   k=order, s=0)
    k_phase_off = scipy.interpolate.UnivariateSpline(cal.freq, k_phase,
                                                     k=order, s=0)

    # interpolation/vector operations are much faster if you cast
    # FrequencySeries to numpy.array
    freq_even = strain_tilde.sample_frequencies.numpy()
    k_even_sample = k_amp_off(freq_even) * \
                    numpy.exp(1.0j * k_phase_off(freq_even))
    strain_tilde_adjusted = pycbc.types.FrequencySeries(
                    strain_tilde.numpy() * k_even_sample,
                    delta_f=strain_tilde.delta_f)

    # IFFT to get time series
    strain_adjusted = strain_tilde_adjusted.to_timeseries()
    strain_adjusted.start_time = strain.start_time

    return strain_adjusted
