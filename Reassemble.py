import madmom
from madmom.features import *
import librosa, librosa.display, numpy
import IPython.display as ipd
from pprint import pprint
import json
import Segment
import utilities
import dbt
from copy import deepcopy
import sys


class Reassemble():

    def __init__(self, song_name1, song_name2):
        self.song_name1 = song_name1
        self.song_name2 = song_name2

        self.song1_segment, self.song1_time_per_chord =  self.prepare_song(song_name1)
        self.song2_segment, self.song2_time_per_chord =  self.prepare_song(song_name2)

    def run(self):
        if self.get_matching_beat():
            self.load_and_rescale()
            self.mash_up()
            self.save_file()

    def prepare_song(self, song_name):
        with open(song_name.replace(".wav", "") + '.json') as f:
            data = json.load(f)
        song_useable_segments = []
        for segment in data:
            if segment['useable']:
                song_useable_segments.append(Segment.Segment().setJSON(segment))
        for segment in song_useable_segments:
            print(segment.toString())
        song_segment = song_useable_segments[0]
        song_time_per_chord = song_segment.average_time_per_beat
        return song_segment, song_time_per_chord


    def load_and_rescale(self):
        #CALCULATE MUTUAL TEMPO
        mutual_time_per_chord = (self.song2_time_per_chord + self.song1_time_per_chord) / 2
        print(self.song_name1 + "'s tempo: " + str(self.song2_time_per_chord))
        print(self.song_name2 + "'s tempo: " + str(self.song1_time_per_chord))
        print("New tempo:", mutual_time_per_chord)

        # LOAD AND RESTRETCH SONG
        self.song1_data,sr = dbt.load_librosa(self.song_name1)
        self.song1_data = utilities.rescale(self.song1_data, mutual_time_per_chord / self.song1_time_per_chord)

        self.song2_data,sr = dbt.load_librosa(self.song_name2.replace(".wav", "") + "_vocal.wav")
        self.song2_data = utilities.rescale(self.song2_data, mutual_time_per_chord / self.song2_time_per_chord)

        def rescale_beat_time(beat_time, ratio):
            return [beat * ratio for beat in beat_time]
        
        # RESTRETCH BEATS
        self.song1_segment.downbeats = rescale_beat_time(self.song1_segment.downbeats, mutual_time_per_chord / self.song1_time_per_chord)
        self.song2_segment.downbeats = rescale_beat_time(self.song2_segment.downbeats, mutual_time_per_chord / self.song2_time_per_chord)
        self.song1_segment.end = len(self.song1_data) / sr
        self.song2_segment.end = len(self.song2_data) / sr
        self.sr = sr


    def get_matching_beat(self):
        import dbt
        chords_1 = self.song1_segment.chords
        chords_2 = self.song2_segment.chords
        matching_result =  dbt.getMatchingChord(chords_2,chords_1)
        if not matching_result:
            print("Cannot find a match")
            self.matching_result = None
            return False
        else:
            self.matching_result = matching_result[0]
            print("Matching result scale:",  self.matching_result[0], "offset", self.matching_result[1])
            return True


    def mash_up(self):
        def shift_pitch(data, shift_tone, sr):
            data = librosa.effects.pitch_shift(data, sr, n_steps=shift_tone)
            return data

        def align(original_data, original_segment, addon_data, addon_segment, shift_idx, sr):
            addon_timeline = addon_segment.downbeats
        #     temp = addon_timeline + [len(addon_data) / sr] #Attempt to undo the -1
        #     addon_timeline = temp
            print("LENGTH ADDON_DATA", len(addon_data), len(addon_data) / sr)
            print("LENGTH ORIGINAL_DATA", len(original_data),"Start", original_segment.start, "End", original_segment.end)
        #     print(addon_timeline)
            
            merge_count_interval = min(len(addon_segment.downbeats), len(original_segment.downbeats) - shift_idx)
            original_data_copy = deepcopy(original_data)
            for idx in range(merge_count_interval - 1): # TODO: undo the -1
                addon_data_slice_start = int(addon_timeline[idx] * sr)
                addon_data_slice_end = int(addon_timeline[idx+1] * sr)
                addon_data_slice = addon_data[addon_data_slice_start: addon_data_slice_end]
                print("addon_data shape", len(addon_data_slice),addon_data_slice_start, addon_data_slice_end, "max_val", max(addon_data_slice))
                
                original_data_slice_start = int((original_segment.start + original_segment.downbeats[idx + shift_idx]) * sr)
                original_data_slice_end = int((original_segment.start + original_segment.downbeats[idx+1 + shift_idx]) * sr)
                original_data_slice = original_data_copy[original_data_slice_start: original_data_slice_end]
                print("original shape", len(original_data_slice), max(original_data_slice))
                
                stretch_factor = (addon_data_slice_end - addon_data_slice_start)/(original_data_slice_end - original_data_slice_start)

                addon_data_slice = librosa.effects.time_stretch(np.array(addon_data_slice), stretch_factor)
                print("addon_data_slice.shape:", addon_data_slice.shape[0])
                if addon_data_slice.shape[0] > len(original_data_slice):
                    addon_data_slice  = addon_data_slice[:len(original_data_slice)]
                elif addon_data_slice.shape[0] < len(original_data_slice):
                    padding = np.zeros(len(original_data_slice) - addon_data_slice.shape[0])
                    addon_data_slice = np.concatenate((addon_data_slice,padding), axis=0)
        #         new_data =  original_data_slice / original_data_slice.max() + addon_data_slice / addon_data_slice.max()
                new_data =  original_data_slice + addon_data_slice * 0.35

                new_data = new_data.tolist()
                print("NEW MASHED UP", len(new_data), max(new_data))
                
                original_data_copy[original_data_slice_start: original_data_slice_end ] = new_data
            return original_data_copy
        
        # shifted_addon_song = shift_pitch(song2_data, matching_result[0], sr)
        shifted_original_song = shift_pitch(self.song1_data, - self.matching_result[0], self.sr)


        # new_song = align(song1_data, song1_segment, shifted_addon_song, song2_segment, matching_result[1], sr)
        self.new_song = align(shifted_original_song, self.song1_segment, self.song2_data, self.song2_segment, self.matching_result[1], self.sr)
    
    def save_file(self):
        out_filename = self.song_name1.replace(".wav","") + "_" + self.song_name2.replace(".wav","") + '.wav'
        librosa.output.write_wav(out_filename, self.new_song, self.sr)
        print("Write to", out_filename)



Reassemble(sys.argv[1], sys.argv[2]).run()