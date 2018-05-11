# Beat tracking example
from __future__ import print_function
import librosa, sys

# 1. Get the file path to the included audio example
filename = sys.argv[1]

y, sr = librosa.load(filename)

y_mono = librosa.core.to_mono(y)
print("Mono shape", y_mono.shape)

outputfile = filename.strip(".wav").strip(".mp3") + "_mono.wav"

librosa.output.write_wav(outputfile, y_mono, sr) 