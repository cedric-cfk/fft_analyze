# Instructions

## fft_with_wav_input
This program reads a wav and analyzes it with fft.

To run it you need a wav file on the SD Card.
Also, you need to change some variables according to the instructions:
```python
WAV_FILE = 'mic-recording_5.wav' # File Name, relative to sd/audio.
SAMPLE_RATE_IN_HZ = 4050 # Same as in the recording
RECORD_TIME_IN_MS = 1000 # Same as in the recording(But in ms not seconds)
```

:warning: **Caution!!** If the number 'NUM_SAMPLE_BYTES_TO_WRITE After:' on your command line is greater than 32768, the program will fail.
