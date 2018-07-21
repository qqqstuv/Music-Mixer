import madmom
from madmom.features import *
import librosa, librosa.display, numpy
import numpy as np
import matplotlib.pyplot as plt
import IPython.display as ipd
from pprint import pprint
import wave
from madmom.audio.signal import load_audio_file
from madmom.audio.signal import resample
from madmom.audio.chroma import DeepChromaProcessor
import bisect

def load_librosa(name):
    data, sr = librosa.load(name)
    return data, sr

def load_madmom(name):
    data, sr = load_audio_file(name)
    return data, sr

def load_and_resample(name):
    data, sr = librosa.load(name)
    data = librosa.resample(data, sr,44100)
    return data, 44100

# The heavy stuff
def extract_downbeat(bpr, data):
    proc = DBNDownBeatTrackingProcessor(beats_per_bar=bpr, fps = 100)
    act = RNNDownBeatProcessor()(data)
    downbeats = proc(act)

    return downbeats

def filter_downbeat(downbeats):
    filtered = downbeats[downbeats[:, 1] == 1] # only care about the first downbeat as the chord changes
    time = filtered[:,0]
    beat_num = filtered[:,1]
    return time, beat_num

def print_and_save_downbeat(file_name, timeline, beat_number, idx=""):
    print("Saving downbeat of", file_name)
    downbeat_file = file_name.replace(".wav", "") + idx + "_downbeat.txt"
    file = open(downbeat_file,"w") 
    for i,j in zip(timeline, beat_number):
#         print("%8.6f\t%8.6f\t%d" % (i,i,j))
        file.write("%8.6f\t%8.6f\t%d\n" % (i,i,j)) 
    file.close()

def print_and_save_chord(file_name, timeline, chord, idx=""):
    print("Saving chords of", file_name)
    downbeat_file = file_name.replace(".wav", "") + idx + "_chord.txt"
    file = open(downbeat_file,"w") 
    for i,j in zip(timeline, chord):
#         print("%8.6f\t%8.6f\t%d" % (i,i,j))
        file.write("%8.6f\t%8.6f\t%s\n" % (i,i,j)) 
    file.close()

def get_chords_old(_time, data, sr):
    time = _time + [len(data) / sr]
    length_result = len(time) - 1
    chord_result = ["" for i in range(length_result)]
    decode = DeepChromaChordRecognitionProcessor()    
    chord_dictionary = dict()
    for i in range(length_result):
        start_frame = int(time[i] * sr)
        end_frame = int(time[i+1] * sr)
        slice_data = data[start_frame: end_frame]
        chroma = DeepChromaProcessor()(slice_data)
        chords = decode(chroma)
        print("index",i,":",time[i], ":",time[i+1],"duration:", time[i+1] - time[i] , chords)
        if len(chords) > 1:
            chords = [[abs(tuple[0] - tuple[1]), tuple[2]] for tuple in chords]
            chord_name = max(chords, key=lambda x:x[0])[1]
            print("Possible error: >1 chord detected", chord_name)
        else:
            chord_name = chords[0][2]
        if chord_name not in chord_dictionary:
            chord_dictionary[chord_name] = []
        chord_dictionary[chord_name].append(i)
        chord_result[i] = chord_name

    return chord_dictionary, chord_result



def get_chords_new(time, data):
    decode = DeepChromaChordRecognitionProcessor()
    chroma = DeepChromaProcessor()(data)
    chords = decode(chroma)
    chord_timeLine = [chord[0] for chord in chords]
    chord_matching_timeLine = [chord[2] for chord in chords]
    for chord in chords:
        print(chord)
    
    length_result = len(time)
    chord_result = ["" for i in range(length_result)]
    chord_dictionary = dict()
    for i in range(length_result):
        idx = bisect.bisect_right(chord_timeLine, time[i]) - 1
        if idx + 1 < len(chord_timeLine):
            idx = int(max(abs(time[i] - chord_timeLine[idx]), abs(time[i] - chord_timeLine[idx+1])))
        chord_result.append(chord_matching_timeLine[idx])
    return chord_dictionary, chord_result

chord_tranposition = ['A', 'A#', 'B', 'C','C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#']
from copy import deepcopy

class Chord:
    def __init__(self, name, modification):
        self.name = name
        self.modification = modification
    def print(self):
        print(self.name + " " + self.modification)
    def __eq__(self, other): 
        return self.name == other.name and self.modification == other.modification
    def toString(self): 
        return self.name + " " + self.modification      
# a = Chord("A","maj")        
# b = Chord("B","maj")        
# print(a==b)

# Get how far each chord is from each other, Return -1 if it's minor/major difference
def transpose_distance(chord_from, chord_to):
    if chord_from.modification != chord_to.modification:
        return -1, False
    else:
        diff = chord_tranposition.index(chord_to.name) - chord_tranposition.index(chord_from.name)
        if 12 - abs(diff) <= abs(diff):
            if diff > 0:
                return - (12 - abs(diff)), True
            else:
                return 12 - abs(diff), True
        else:
            return diff, True

def transpose(chord, amount):
    new_idx = (chord_tranposition.index(chord.name) + amount) % 12
    # print("tranpose to", chord_tranposition.index(chord.name), amount)
    return chord_tranposition[new_idx]


def compare(chords1, chords2):
    for i in range(len(chords2) - len(chords1)):
        isEqual = True
        compare_i = i 
        for j in range(len(chords1)):
            # print("comparing", chords1[j].toString(), chords2[compare_i].toString(), chords2[compare_i] != chords1[j])
            if chords2[compare_i] != chords1[j]:
                isEqual = False
                break
            compare_i += 1
        if isEqual:
            return i
    return -1


#What get passed in this function must be an unified chord sequence. I only take the first {chord_num}(4) samples from chords1
def getMatchingChord(chords1, chords2, chord_num=4):
    chords1 = [Chord(i.split(":")[0], i.split(":")[1]) for i in chords1]
    chords2 = [Chord(i.split(":")[0], i.split(":")[1]) for i in chords2]
    print("chords1", [chord1.toString() for chord1 in chords1])
    print("chords2", [chord1.toString() for chord1 in chords2])
    
    possible_result = []
    for idx in range(chord_num):
        transposeDistance, isMatch = transpose_distance(chords1[idx], chords2[0]) # find transpose from chord_1 to first of chord_2
        if isMatch:
            print("transpose_distance:",  transposeDistance, "from", chords1[idx].name, "to", chords2[0].name)
            temp_chords1 = deepcopy(chords1[:chord_num])
            for temp_idx in range(len(temp_chords1)):
                temp_chords1[temp_idx].name = transpose(temp_chords1[temp_idx], transposeDistance)
            print("temp_chords1", [chord1.toString() for chord1 in temp_chords1])
            found = compare(temp_chords1, chords2)
            print("Found", found)
            if found != -1:
                possible_result.append([transposeDistance, found])
    return possible_result
            

# _chords2 = ['D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj', 'A#:maj', 'C:min', 'G#:maj', 'D#:maj']

# _chords1 = ['D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj', 'D#:min', 'B:maj', 'F#:maj', 'C#:maj']

# print(getMatchingChord(_chords1, _chords2))