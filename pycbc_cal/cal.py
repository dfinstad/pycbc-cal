import numpy as np

class Calibration:
    """Methods for calibrating/recalibrating GW detector data.
    """
    
    def __init__(self, freq=None, invC0=None, C0=None, D0=None, Atst0=None, Apu0=None, fc0=None):
        """Initialize the detector with the transfer functions for a given epoch
        that starts at time t0.
        
        Parameters
        ----------
        freq : array
            The frquencies corresponding to the values of C0, D0, A0
        invC0 : array
            Initial inverse sensing function 1/C0 at t0 for the frequencies freq.
            Supply either invC0 or C0.
        C0 : array
            Initial sensing function at t0 for the frequencies freq.
            Supply either invC0 or C0.
        D0 : array
            Digital filter for the frequencies freq
        Atst0 : array
            Initial actuation function for the test mass at t0 for the frequencies freq
        Apu0 : array
            Initial actuation function at the penultimate mass stage at t0 for the frequencies freq
        fc0 : float
            Coupled-cavity (CC) pole at time t0 when C0=C(t0) and A0=A(t0) are measured
        """
        
        # Just in case freqarray is complex128 but with 0 imaginary part:
        self.freq = np.real(freq)
        
        if invC0 is not None:
            self.invC0 = invC0
            self.C0 = 1.0/invC0
        if C0 is not None:
            self.invC0 = 1.0/C0
            self.C0 = C0
        
        self.D0 = D0
        self.Atst0 = Atst0
        self.Apu0 = Apu0
        self.fc0 = fc0
        
        # Calculate initial open loop gain
        self.G0 = self.C0 * self.D0 * (self.Atst0 + self.Apu0)
        
        # Calculate initial response function
        self.R0 = (1.0 + self.G0) / self.C0
        
        # Calculate the residual of C0 after factoring out the CC pole fc0 
        # if using the new calibration convention where fc0 is defined
        if fc0 is not None:
            self.Cres = self.C0 * (1 + 1.0j*self.freq/fc0)

    def update_C(self, deltafc=0.0, kc=1.0):
        """Calculate the sensing function C(f,t) given the new parameters 
        kappa_C(t), kappa_A(t), and \Delta f_c(t) = f_c(t) - f_c(t_0)
        
        Parameters
        ----------
        deltafc : float
            Change in coupled-cavity (CC) pole at a time t: \Delta f_c(t) = f_c(t) - f_c(t_0)
        kc : float
            Scalar correction factor for sensing function at time t
        
        Returns
        -------
        C : array
            The new sensing function C(f,t)
        """
        fc = self.fc0 + deltafc
        return self.Cres * kc/(1+1.0j*self.freq/fc)
    
    def update_G(self, deltafc=0.0, kc=1.0, ktst=1.0, kpu=1.0, ktstim=0.0, kpuim=0.0):
        """Calculate the open loop gain G(f,t) given the new parameters 
        kappa_C(t), kappa_A(t), and \Delta f_c(t) = f_c(t) - f_c(t_0)
        
        Parameters
        ----------
        deltafc : float
            Change in coupled-cavity (CC) pole at a time t: \Delta f_c(t) = f_c(t) - f_c(t_0)
        kc : float
            Scalar correction factor for sensing function C at time t
        ktst : float
            Real part of scalar correction factor for actuation function Atst0 at time t
        kpu : float
            Real part of scalar correction factor for actuation function Apu0 at time t
        ktstim : float
            Imaginary part of scalar correction factor for actuation function Atst0 at time t
        kpuim : float
            Imaginary part of scalar correction factor for actuation function Apu0 at time t
        
        Returns
        -------
        G : array
            The new open loop gain G(f,t)
        """
        
        C = self.update_C(deltafc=deltafc, kc=kc)
        A = self.Atst0 * (ktst+1.0j*ktstim) + self.Apu0 * (kpu+1.0j*kpuim)
        return C * self.D0 * A

    
    def update_R(self, deltafc=0.0, kc=1.0, ktst=1.0, kpu=1.0, ktstim=0.0, kpuim=0.0):
        """Calculate the response function R(f,t) given the new parameters 
        kappa_C(t), kappa_A(t), and \Delta f_c(t) = f_c(t) - f_c(t_0)
        
        Parameters
        ----------
        deltafc : float
            Change in coupled-cavity (CC) pole at a time t: \Delta f_c(t) = f_c(t) - f_c(t_0)
        kc : float
            Scalar correction factor for sensing function at time t
        ktst : float
            Real part of scalar correction factor for actuation function Atst0 at time t
        kpu : float
            Real part of scalar correction factor for actuation function Apu0 at time t
        ktstim : float
            Imaginary part of scalar correction factor for actuation function Atst0 at time t
        kpuim : float
            Imaginary part of scalar correction factor for actuation function Apu0 at time t

        Returns
        -------
        R : array
            The new response function R(f,t)
        """
        
        C = self.update_C(deltafc=deltafc, kc=kc)
        G = self.update_G(deltafc=deltafc, kc=kc, ktst=ktst, kpu=kpu, ktstim=ktstim, kpuim=kpuim)
        
        return (1.0 + G) / C
