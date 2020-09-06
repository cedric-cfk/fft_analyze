import ulab as np
from ulab import vector
from ulab import numerical
from ulab import fft
import math
from machine import SD
import utime

bins = 100

Fs = 1000                   # Sampling frequency
T = 1/Fs                    # Sampling period
L = 2048                    # Length of signal
t = np.array(range(0,L))*T  # Time vector

S = 0.7*vector.sin(2*math.pi*50*t) + vector.sin(2*math.pi*120*t)

f = Fs*np.array(range(0,(L//2)+1))/L

try:
    start_time = utime.ticks_ms()
    a,b = fft.fft(S)
    print('fft finished')
    a = a/L
    b = b/L
    P2 = vector.sqrt(a*a + b*b)

    P1 = P2[:L//2+1]

    P1[1:(P1.size() - 1)] = 2*P1[1:(P1.size() - 1)]
    #print(P1)
    #print(P1.size())

    #print(f.size())
    result = []
    bins = int(bins / f[1])
    print('Bins size: \t', bins)
    for x in range(0,10):
        min = (bins*x)
        max = ((bins*(x+1)) - 1)
        #print(max)
        if max < P1.size():
            ar = P1[min:max]
            sda = numerical.max(ar)
            result += [sda]
        elif min < P1.size():
            ar = P1[min:P1.size()-1]
            sda = numerical.max(ar)
            result += [sda]
        else:
            result += [0]
    time_needed = utime.ticks_diff(utime.ticks_ms(), start_time)
    print("--- %s milliseconds ---" % time_needed)
    print("result: ", result)
except Exception as e:
    print('caught exception {} {}'.format(type(e).__name__, e))
