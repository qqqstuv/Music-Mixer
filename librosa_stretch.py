# Beat tracking example
from __future__ import print_function
import librosa, sys

# 1. Get the file path to the included audio example
filename = sys.argv[1]
original = float(sys.argv[2])
new = float(sys.argv[3])
ratio = new / original
# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(filename)

y_fast = librosa.effects.time_stretch(y, ratio)

outputfile = filename.strip(".wav").strip(".mp3") + "_stretch.wav"

librosa.output.write_wav(outputfile, y_fast, sr) 