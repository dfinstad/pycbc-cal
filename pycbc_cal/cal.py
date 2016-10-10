""" Classes and functions for adjusting strain data.
"""

import numpy

class Calibration:
    """ Class for adjusting time-varying calibration parameters of strain data.
    """
    
    def __init__(self, freq=None, fc0=None, invc0=None, c0=None, d0=None,
                 a_tst0=None, a_pu0=None):
        """ Initialize the class with the transfer functions for a given epoch
        that starts at time t0.
        
        Parameters
        ----------
        freq : array
            The frquencies corresponding to the values of c0, d0, a0 in Hertz.
        fc0 : float
            Coupled-cavity (CC) pole at time t0 when c0=c(t0) and a0=a(t0)
            are measured.
        invc0 : array
            Initial inverse sensing function 1/c0 at t0 for the frequencies.
            Supply either invC0 or C0.
        c0 : array
            Initial sensing function at t0 for the frequencies.
            Supply either invc0 or c0.
        d0 : array
            Digital filter for the frequencies.
        a_tst0 : array
            Initial actuation function for the test mass at t0 for the
            frequencies.
        a_pu0 : array
            Initial actuation function at the penultimate mass stage at t0 for
            the frequencies.
        """

        # cast frequencies to real numbers
        self.freq = numpy.real(freq)

        # set initial sensing function and its inverse
        if invc0 is not None:
            self.invc0 = invc0
            self.c0 = 1.0 / invc0
        if c0 is not None:
            self.invc0 = 1.0 / c0
            self.c0 = c0

        # set the other initial transfer functions
        self.d0 = d0
        self.a_tst0 = a_tst0
        self.a_pu0 = a_pu0
        self.fc0 = fc0
        
        # calculate initial open loop gain
        self.g0 = self.c0 * self.d0 * (self.a_tst0 + self.a_pu0)
        
        # calculate initial response function
        self.r0 = (1.0 + self.g0) / self.c0
        
        # calculate the residual of c0 after factoring out the CC pole fc0 
        # if using the new calibration convention where fc0 is defined
        if fc0 is not None:
            self.c_res = self.c0 * (1 + 1.0j * self.freq / fc0)


    def update_c(self, delta_fc=0.0, kappa_c=1.0):
        """ Calculate the sensing function c(f,t) given the new parameters 
        kappa_c(t), kappa_a(t), and \Delta f_c(t) = f_c(t) - f_c(t_0).
        
        Parameters
        ----------
        delta_fc : float
            Change in coupled-cavity (CC) pole at a time t:
            \Delta f_c(t) = f_c(t) - f_c(t_0).
        kappa_c : float
            Scalar correction factor for sensing function at time t.
        
        Returns
        -------
        c : numpy.array
            The new sensing function c(f,t).
        """
        fc = self.fc0 + delta_fc
        return self.c_res * kappa_c / (1 + 1.0j * self.freq / fc)
    
    def update_g(self, delta_fc=0.0, kappa_c=1.0,
                 kappa_tst_re=1.0, kappa_tst_im=0.0,
                 kappa_pu_re=1.0, kappa_pu_im=0.0):
        """ Calculate the open loop gain g(f,t) given the new parameters 
        kappa_c(t), kappa_a(t), and \Delta f_c(t) = f_c(t) - f_c(t_0).
        
        Parameters
        ----------
        delta_fc : float
            Change in coupled-cavity (CC) pole at a time t:
            \Delta f_c(t) = f_c(t) - f_c(t_0).
        kappa_c : float
            Scalar correction factor for sensing function c at time t.
        kappa_tst_re : float
            Real part of scalar correction factor for actuation function
            a_tst0 at time t.
        kappa_pu_re : float
            Real part of scalar correction factor for actuation function
            a_pu0 at time t.
        kappa_tst_im : float
            Imaginary part of scalar correction factor for actuation function
            a_tst0 at time t.
        kappa_pu_im : float
            Imaginary part of scalar correction factor for actuation function
            a_pu0 at time t.
        
        Returns
        -------
        g : numpy.array
            The new open loop gain g(f,t).
        """
        c = self.update_c(delta_fc=delta_fc, kappa_c=kappa_c)
        a_tst = self.a_tst0 * (kappa_tst_re + 1.0j * kappa_tst_im)
        a_pu = self.a_pu0 * (kappa_pu_re + 1.0j * kappa_pu_im)
        return c * self.d0 * (a_tst + a_pu)

    
    def update_r(self, delta_fc=0.0, kappa_c=1.0,
                 kappa_tst_re=1.0, kappa_tst_im=0.0,
                 kappa_pu_re=1.0, kappa_pu_im=0.0):
        """ Calculate the response function R(f,t) given the new parameters 
        kappa_c(t), kappa_a(t), and \Delta f_c(t) = f_c(t) - f_c(t_0).

        Parameters
        ----------
        delta_fc : float
            Change in coupled-cavity (CC) pole at a time t:
            \Delta f_c(t) = f_c(t) - f_c(t_0).
        kappa_c : float
            Scalar correction factor for sensing function c at time t.
        kappa_tst_re : float
            Real part of scalar correction factor for actuation function
            a_tst0 at time t.
        kappa_pu_re : float
            Real part of scalar correction factor for actuation function
            a_pu0 at time t.
        kappa_tst_im : float
            Imaginary part of scalar correction factor for actuation function
            a_tst0 at time t.
        kappa_pu_im : float
            Imaginary part of scalar correction factor for actuation function
            a_pu0 at time t.

        Returns
        -------
        r : numpy.array
            The new response function r(f,t).
        """
        c = self.update_c(delta_fc=delta_fc, kappa_c=kappa_c)
        g = self.update_g(delta_fc=delta_fc, kappa_c=kappa_c,
                          kappa_tst_re=kappa_tst_re, kappa_tst_im=kappa_tst_im,
                          kappa_pu_re=kappa_pu_re, kappa_pu_im=kappa_pu_im)
        return (1.0 + g) / c
