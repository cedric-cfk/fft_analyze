# The MIT License (MIT)
# Copyright (c) 2019 Michael Shi
# Copyright (c) 2020 Mike Teachman
# https://opensource.org/licenses/MIT

# Purpose:
# - read 32-bit audio samples from the left channel of an I2S microphone
# - snip upper 16-bits from each 32-bit microphone sample
# - write 16-bit samples to a SD card file using WAV format
#
# Recorded WAV file is named:
#   "mic_left_channel_16bits.wav"
#
# Hardware tested:
# - INMP441 microphone module
# - MSM261S4030H0 microphone module

import os
import utime
import ulab as np
from machine import Pin
from machine import SD
from machine import I2S
from ulab import fft
from ulab import vector
import math
import sys

#======= USER CONFIGURATION =======
RECORD_TIME_IN_MS = 10
SAMPLE_RATE_IN_HZ = 4050
#======= USER CONFIGURATION =======

SAMPLE_SIZE_IN_BITS = 32
SAMPLE_SIZE_IN_BYTES = SAMPLE_SIZE_IN_BITS // 8
MIC_SAMPLE_BUFFER_SIZE_IN_BYTES = 4096
NUM_SAMPLE_BYTES_TO_WRITE = int((RECORD_TIME_IN_MS / 1000) * SAMPLE_RATE_IN_HZ * SAMPLE_SIZE_IN_BYTES)
NUM_SAMPLES_IN_DMA_BUFFER = 256
NUM_CHANNELS = 1

#======= Analyzer Settings =======
bins = 100

# Calculate next higher power of 2 to NUM_SAMPLE_BYTES_TO_WRITE.
print(NUM_SAMPLE_BYTES_TO_WRITE)
def bitLenCount(int_type):
    length = 0
    count = 0
    while (int_type):
        count += (int_type & 1)
        length += 1
        int_type >>= 1
    return math.pow(2, length)
SAMPLE_RATE_IN_HZ = int(bitLenCount(NUM_SAMPLE_BYTES_TO_WRITE) // (SAMPLE_SIZE_IN_BYTES * (RECORD_TIME_IN_MS / 1000)))
NUM_SAMPLE_BYTES_TO_WRITE = int((RECORD_TIME_IN_MS / 1000) * SAMPLE_RATE_IN_HZ * SAMPLE_SIZE_IN_BYTES)
print(NUM_SAMPLE_BYTES_TO_WRITE)


Fs = SAMPLE_RATE_IN_HZ#1230 # Sampling frequency
T = 1/Fs                    # Sampling period


# I2S pins
bck_pin = Pin('P11')
ws_pin = Pin('P22')
sdin_pin = Pin('P21')

audio_in = I2S(
    I2S.NUM0,
    bck=bck_pin, ws=ws_pin, sdin=sdin_pin,
    standard=I2S.PHILIPS,
    mode=I2S.MASTER_RX,
    dataformat=I2S.B32,
    channelformat=I2S.ONLY_LEFT,
    samplerate=SAMPLE_RATE_IN_HZ,
    dmacount=50,
    dmalen=NUM_SAMPLES_IN_DMA_BUFFER
)

# configure SD card
#   slot=2 configures SD card to use the SPI3 controller (VSPI), DMA channel = 2
#   slot=3 configures SD card to use the SPI2 controller (HSPI), DMA channel = 1
sd = SD()
try:
    os.mount(sd, "/sd")
except:
    print('sd already mounted')
# create audio dir in case it does not exist
try:
    os.stat('/sd/audio')
except:
    os.mkdir('/sd/audio')

total_time = 0

for i in range(1, 6):
    #txt = open('/sd/audio/fft-to-recording_'+str(i)+'.txt','wb')
    #txt = open('/sd/audio/fft-to-recording_'+str(i)+'.txt','w')

    # allocate sample arrays
    #   memoryview used to reduce heap allocation in while loop
    print((sys.maxsize//2))
    mic_samples = bytearray(4096)
    mic_samples_mv = memoryview(mic_samples)
    #store_samples = bytearray(41823)
    #store_samples_mv = memoryview(store_samples)
    print(list(mic_samples_mv[:2]))

    num_sample_bytes_written = 0

    # make the LED light up in red color
    #pycom.rgbled(0x111100)
    #time.sleep(0.5)
    #pycom.rgbled(0x110000)
    print('#'+str(i)+' starting...')
    start_time = utime.ticks_ms()
    # read 32-bit samples from I2S microphone, snip upper 16-bits, write snipped samples to WAV file
    start = True
    while num_sample_bytes_written < NUM_SAMPLE_BYTES_TO_WRITE:

        try:
            # try to read a block of samples from the I2S microphone
            # readinto() method returns 0 if no DMA buffer is full
            start_time_2 = utime.ticks_ms()
            num_bytes_read_from_mic = audio_in.readinto(mic_samples_mv, timeout=RECORD_TIME_IN_MS)
            print(utime.ticks_ms() - start_time_2, "ms")

            print(len(list(mic_samples_mv)))
            print(num_bytes_read_from_mic)

            #if(num_bytes_read_from_mic > 0)

                #store_samples_mv[num_sample_bytes_written:num_bytes_read_from_mic] = #mic_samples_mv[:num_bytes_read_from_mic-1]

                #num_sample_bytes_written += num_bytes_read_from_mic

            if start:
                start = False
            else:
                #print('Test:')
                #print(mic_samples[num_bytes_read_from_mic-20:num_bytes_read_from_mic-1])
                #print(mic_samples[num_bytes_read_from_mic:num_bytes_read_from_mic+500])
                print()

            '''
            if num_bytes_read_from_mic > 0:
                L = num_bytes_read_from_mic # Length of signal
                t = np.array(range(0,L))*T  # Time vector in ms

                f = Fs*np.array(range(0,(L//2)+1))/L

                #calculate fft
                print(num_bytes_read_from_mic)
                try:
                    real, imaginary = fft.fft(np.array(list(mic_samples_mv[:num_bytes_read_from_mic])))
                    print('fft finished')
                    real = real/L
                    imaginary = imaginary/L
                    P2 = vector.sqrt(real*real + imaginary*imaginary)

                    P1 = P2[:L//2+1]

                    P1[1:(P1.size() - 1)] = 2*P1[1:(P1.size() - 1)]
                    print(P1)
                    print(P1.size())

                    print(f.size())
                    result = []
                    bins = int(bins / f[1])
                    print('Bins: \t', bins)
                    for x in range(0,10):
                        min = (bins*x)
                        max = ((bins*(x+1)) - 1)
                        print(max)
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
                    num_sample_bytes_written += num_bytes_read_from_mic
                except ValueError:
                    pass
                    '''
        except (KeyboardInterrupt, Exception) as e:
            print('caught exception {} {}'.format(type(e).__name__, e))
            audio_in.deinit()
            break

    time_needed = utime.ticks_diff(utime.ticks_ms(), start_time)
    print("--- %s milliseconds ---" % time_needed)
    total_time += time_needed
    #txt.close()
    # do not unmount and deinit SD in case you want to read files via WiFi and a FTP connection
    #os.umount("/sd")
    #sd.deinit()

    print('#'+str(i)+' ... done! -- %d sample bytes written to txt file' % num_sample_bytes_written)
    print()

    # make the LED light up in green color
    #pycom.rgbled(0x000000)
    #time.sleep(0.5)
    #pycom.rgbled(0x001100)

    #time.sleep(2)
# do not deinit audio in case you will record an other round

print('All done!')

print('Time needed for all calculations: \t', total_time, 'milliseconds\nAverage Time needed: \t', (total_time/5), 'milliseconds')