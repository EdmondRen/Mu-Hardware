def roll_zeropad(a, shift, axis=None):
    """
    Roll array elements along a given axis.

    Elements off the end of the array are treated as zeros.

    Parameters
    ----------
    a : array_like
        Input array.
    shift : int
        The number of places by which elements are shifted.
    axis : int, optional
        The axis along which elements are shifted.  By default, the array
        is flattened before shifting, after which the original
        shape is restored.

    Returns
    -------
    res : ndarray
        Output array, with the same shape as `a`.

    See Also
    --------
    roll     : Elements that roll off one end come back on the other.
    rollaxis : Roll the specified axis backwards, until it lies in a
               given position.

    Examples
    --------
    >>> x = np.arange(10)
    >>> roll_zeropad(x, 2)
    array([0, 0, 0, 1, 2, 3, 4, 5, 6, 7])
    >>> roll_zeropad(x, -2)
    array([2, 3, 4, 5, 6, 7, 8, 9, 0, 0])

    """
    a = np.asanyarray(a)
    if shift == 0: return a
    if axis is None:
        n = a.size
        reshape = True
    else:
        n = a.shape[axis]
        reshape = False
    if np.abs(shift) > n:
        res = np.zeros_like(a)
    elif shift < 0:
        shift += n
        zeros = np.zeros_like(a.take(np.arange(n-shift), axis))
        res = np.concatenate((a.take(np.arange(n-shift,n), axis), zeros), axis)
    else:
        zeros = np.zeros_like(a.take(np.arange(n-shift,n), axis))
        res = np.concatenate((zeros, a.take(np.arange(n-shift), axis)), axis)
    if reshape:
        return res.reshape(a.shape)
    else:
        return res
    
    
def Pulse2(x, tau_r, tau_f1, tau_f2, A1, A2, t0, A0):
    # Test: plot(np.linspace(-50,50,200), Pulse3(np.linspace(-50,50,200), 2,4,10,20,3,2,1,10.5,5))
    times=x-t0
    mask =times>0
    pulse = (A1     *     (np.exp(-times[mask] / tau_f1))
            +A2     *     (np.exp(-times[mask] / tau_f2))
            -(A1+A2) * (np.exp(-times[mask] / tau_r))
            )
    pulse = np.concatenate((np.zeros(sum(~mask)), pulse))
    pulse/=max(pulse)
    pulse*=A0
    return pulse



def sim_trigger_threshold(t_fiber = 2.1,t_scint = 5.2,signal_npe = 6,
                          threshold_list = [0,1,2],
                          sipm_pulseshape_time = [], sipm_pulseshape_voltage=[],
                          N_sample= 10_000):
    """
    Calculate the trigger threshold on real events given a treshold set on dark current in unit of pe.
    The real event is smeared out because of the time constants
    
    Return: 
        trigger_time: with dimesion of (N_sample, len(threshold))
    """
    t_sample_fiber = np.random.exponential(t_fiber, (N_sample,signal_npe))
    t_sample_scint = np.random.exponential(t_scint, (N_sample,signal_npe))
    t_sample = np.sort(t_sample_fiber+t_sample_scint, axis=1)
    
    time_max = max(sipm_pulseshape_time)
    time_interval = sipm_pulseshape_time[0]
    trigger_time = np.zeros((N_sample, len(threshold_list)))
    pulse_template = sipm_pulseshape_voltage/max(sipm_pulseshape_voltage)
    for ievent in range(N_sample):
        # Make the artificial pulse
        pulse = np.zeros_like(sipm_pulseshape_time)
        for t in t_sample[ievent]:
            pulse += roll_zeropad(pulse_template, int(t//time_interval))
            
        # Find trigger threshold
        trigger_time[i] = [np.argmax(pulse>np.floor(th)+0.5) for th in threshold_list]
     
    return trigger_time

def process_dt(trigger_time):
    """
    Return: 
        dt_width: equivalent sigma of single channel, 1-D list with length of (len(threshold))
    """    
    t = trigger_time
    dt = (t[:len(t)//2]- t[len(t)//2:])/np.sqrt(2)
    # Use the width of middle 76% quantile to estimate the sigma
    dt_width = np.diff(np.quantile(dt, [0.115, 1-0.115], axis=0), axis=0)/(2*np.sqrt(2*np.log(2)))
    
    return dt_width



# Physics parameter
# t_fiber = 2.1
t_scint = 6

# Simulation setting
N_sample= 10_000

# Parameters to scan:
threshold_list = [0,1,2,3]
signal_npe_list = np.arange(4,25)
t_fiber_list   = [1.5, 2, 3, 4, 5, 6, 7, 8]

pulse_template_t = np.linspace(-10,60,1000)
pulse_template = Pulse2(pulse_template_t, )
