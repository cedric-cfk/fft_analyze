import os
import utime
import ulab as np
from machine import Pin
from machine import SD
from machine import I2S
from ulab import fft
from ulab import vector
from ulab import numerical
import math
import sys


#======= USER CONFIGURATION =======
WAV_FILE = 'mic-recording_5.wav' # File Name, relativ to sd/audio.
SAMPLE_RATE_IN_HZ = 4050 # Same as in the recording
RECORD_TIME_IN_MS = 1000 # Same as in the recording(But in ms not seconds)
#======= USER CONFIGURATION =======
SAMPLE_SIZE_IN_BITS = 16
SAMPLE_SIZE_IN_BYTES = SAMPLE_SIZE_IN_BITS // 8
MIC_SAMPLE_BUFFER_SIZE_IN_BYTES = 4096
NUM_SAMPLE_BYTES_TO_WRITE = int((RECORD_TIME_IN_MS / 1000) * SAMPLE_RATE_IN_HZ * SAMPLE_SIZE_IN_BYTES) # 32768 MAX!
NUM_SAMPLES_IN_DMA_BUFFER = 256
NUM_CHANNELS = 1

L = NUM_SAMPLE_BYTES_TO_WRITE // 2  # Length of signal

#======= Analyzer Settings =======
BINS = 100
START_AT_HZ = 0
NUMBER_OF_BINS = 10

def bitLenCount(int_type):
    length = 0
    count = 0
    while (int_type):
        count += (int_type & 1)
        length += 1
        int_type >>= 1
    return math.pow(2, length-1)
L = int(bitLenCount(L))
NUM_SAMPLE_BYTES_TO_WRITE = int(bitLenCount(L)) * 2
RECORD_TIME_IN_MS = int((NUM_SAMPLE_BYTES_TO_WRITE * 1000) // (SAMPLE_SIZE_IN_BYTES * SAMPLE_RATE_IN_HZ))
print("NUM_SAMPLE_BYTES_TO_WRITE After: \t", NUM_SAMPLE_BYTES_TO_WRITE)
print()


Fs = SAMPLE_RATE_IN_HZ#1230 # Sampling frequency
T = 1/Fs                    # Sampling period

#t = np.array(range(0,L))*T  # Time vector in ms

f = Fs*np.array(range(0,(L//2)+1))/L

bins = int(BINS / f[1])
start_at_hz = int(START_AT_HZ / f[1])

'''
bck_pin = Pin(21)
ws_pin = Pin(22)
sdout_pin = Pin(27)
'''
# channelformat settings:
#     mono WAV:  channelformat=I2S.ONLY_LEFT
'''
audio_out = I2S(
    I2S.NUM0,
    bck=bck_pin, ws=ws_pin, sdout=sdout_pin,
    standard=I2S.PHILIPS,
    mode=I2S.MASTER_TX,
    dataformat=I2S.B16,
    channelformat=I2S.ONLY_LEFT,
    samplerate=SAMPLE_RATE_IN_HZ,
    dmacount=10, dmalen=512)
'''

# configure SD card
#   slot=2 configures SD card to use the SPI3 controller (VSPI), DMA channel = 2
#   slot=3 configures SD card to use the SPI2 controller (HSPI), DMA channel = 1
sd = SD()
try:
    os.mount(sd, "/sd")
except:
    print('sd already mounted')

wav_file = '/sd/audio/{}'.format(WAV_FILE)
wav = open(wav_file,'rb')

# advance to first byte of Data section in WAV file
pos = wav.seek(44)

# allocate sample arrays
#   memoryview used to reduce heap allocation in while loop
wav_samples = bytearray(1024)
wav_samples_mv = memoryview(wav_samples)
store_samples = bytearray(NUM_SAMPLE_BYTES_TO_WRITE)
store_samples_mv = memoryview(store_samples)

print('Starting')
# continuously read audio samples from the WAV file
# and write them to an I2S DAC

while(True):
    try:
        num_read = wav.readinto(store_samples_mv)
        # end of WAV file? Than break while.
        if num_read == 0:
            print('break')
            break

        # fft analysis
        try:
            real, imaginary = fft.fft(np.array(list(store_samples_mv)))
            #real, imaginary = fft.fft(np.array(list(mic_samples_mv[:num_bytes_read_from_mic])))
            print('fft finished')
            real = real/L
            imaginary = imaginary/L
            P2 = vector.sqrt(real*real + imaginary*imaginary)
            print('average power: ', P2[0])
            P1 = P2[1:L//2+1]

            P1[:(P1.size() - 1)] = 2*P1[:(P1.size() - 1)]

            #print(P1)
            #print(P1.size())
            #print(P1[P1.size() - 10:P1.size() - 1])
            #print(f.size())
            result = []
            #print('Bins: \t', bins)
            for x in range(0,NUMBER_OF_BINS):
                min = (start_at_hz + bins * x)
                max = (start_at_hz + (bins*(x+1)) - 1)
                #print(max)
                if max < P1.size():
                    rang = P1[min:max]
                    #max = numerical.max(rang)
                    max = sum(rang) / len(rang)
                    result += [max]
                elif min < P1.size():
                    rang = P1[min:P1.size()-1]
                    max = numerical.max(rang)
                    #max = sum(rang) / len(rang)
                    result += [max]
                else:
                    result += [0]
            print("result: \t", result)
        except ValueError:
            print("Value Error! is NUM_SAMPLE_BYTES_TO_WRITE power of 2?")
        break
    except (KeyboardInterrupt, Exception) as e:
        print('caught exception {} {}'.format(type(e).__name__, e))
        break

wav.close()
os.umount("/sd")
sd.deinit()
#audio_out.deinit()
print('Done')
