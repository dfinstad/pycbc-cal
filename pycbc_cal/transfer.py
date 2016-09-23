import numpy as np

def zpk_file_to_array(filename):
    """Convert the contents of a zpk file with the columns in
    format [freq, real(tf), imag(tf)] to an array with columns in
    format [freq, real(tf)+j*imag(tf)].
    """
    data = np.loadtxt(filename)
    freq = data[:, 0]
    tf = data[:, 1] + 1.0j*data[:, 2]
    return np.array([freq, tf]).transpose()

