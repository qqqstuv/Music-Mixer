from __future__ import print_function
import librosa 
import librosa.display
import sys, numpy 
import matplotlib.pyplot as plt
import numpy as np

# 1. Get the file path to the included audio example
filename = sys.argv[1]

# 2. Load the audio as a waveform `y`
#    Store the sampling rate as `sr`
y, sr = librosa.load(filename)


fmin = librosa.midi_to_hz(36)
hop_length = 512
C = librosa.cqt(y, sr=sr, fmin=fmin, n_bins=72, hop_length=hop_length)

# logC = librosa.amplitude_to_db(numpy.abs(C))
# plt.figure(figsize=(15, 5))
# librosa.display.specshow(logC, sr=sr, x_axis='time', y_axis='cqt_note', fmin=fmin, cmap='coolwarm')

# print("reach")
# plt.show()


chromagram = librosa.feature.chroma_stft(y, sr=sr, hop_length=hop_length)
plt.figure(figsize=(15, 5))
librosa.display.specshow(chromagram, x_axis='time', y_axis='chroma', hop_length=hop_length, cmap='coolwarm')
# plt.show()

# plt.figure()
# tempo, beat_f = librosa.beat.beat_track(y=y, sr=sr, trim=False)
# beat_f = librosa.util.fix_frames(beat_f, x_max=C.shape[1])
# Csync = librosa.util.sync(C, beat_f, aggregate=np.median)
# beat_t = librosa.frames_to_time(beat_f, sr=sr)
# ax1 = plt.subplot(2,1,1)
# librosa.display.specshow(C, y_axis='chroma', x_axis='time')
# plt.title('Chroma (linear time)')
# ax2 = plt.subplot(2,1,2, sharex=ax1)
# librosa.display.specshow(Csync, y_axis='chroma', x_axis='time', x_coords=beat_t)
# plt.title('Chroma (beat time)')
# plt.tight_layout()

plt.show()
plt.savefig(filename + ".png")