import dbt
import json
import IPython.display as ipd
import utilities
import Segment
import Alignment
import librosa

import sys


def fullExtract(song_name):
    if not song_name:
        return

    json_song_name = song_name.replace(".wav", "") + ".json"
    with open(json_song_name, "w") as json_file:
        dump_data = []
        song_data, sr  = dbt.load_and_resample(song_name)
        song_data = librosa.effects.harmonic(song_data)
        song_segments = [Segment.Segment(0, len(song_data) / sr, "")]
        for idx in range(len(song_segments)):
            print("Loaded song_data with sr", sr, "length", len(song_data) / sr)
            print("Segment info:", song_segments[idx].toString(), "idx", idx)

            #Get Downbeats
            downbeats = dbt.extract_downbeat(4,song_data)        
            time, beat_num = downbeats[:,0].tolist(), downbeats[:,1].tolist()

            print("Number of beats", len(time))
            #Get Chords
            chord_dict, chord_result = dbt.get_chords_old(time, song_data, sr, False)
            #Smoothen the chords
            print("Detected Chords",chord_result)
            new_chord_result, isAligned = Alignment.chord_alignment(chord_result)
            song_segments[idx].useable = isAligned
            
            #Squash the same beats together
            if isAligned:
                boolean_array = [False for i in range(len(new_chord_result))]
                for i in range(len(new_chord_result)):
                    if i == 0 or new_chord_result[i] != new_chord_result[i-1]:
                        boolean_array[i] = True
                new_chords = []
                new_time = []
                for i in range(len(boolean_array)):
                    if boolean_array[i]:
                        new_chords.append(new_chord_result[i])
                        new_time.append(time[i])
                new_chord_result = new_chords
                time = new_time
                
            #Average time per beat
            avg_time_beat = 0
            for i in range(len(time) - 1):
                avg_time_beat += time[i+1] - time[i]
            avg_time_beat = avg_time_beat / len(time)
            print("Average time_per_chord", avg_time_beat)
            
            if not isAligned:
                print("Failed to align chord")
    
            #Write to json object
            song_segments[idx].chords = new_chord_result
            song_segments[idx].downbeats = time
            song_segments[idx].average_time_per_beat = avg_time_beat
            beat_num = [1 for i in range(len(time))]

            #Write to chords and downbeat (for debug)
            dbt.print_and_save_chord(song_name, time, song_segments[idx].chords, str(idx) )
            dbt.print_and_save_downbeat(song_name, time, beat_num, str(idx))
            
            dump_data.append(song_segments[idx].getJSON())    
        json.dump(dump_data, json_file, indent=4)
            

def debugExtract(song_name):
    #Raw, debug
    sample,sr = dbt.load_and_resample(song_name)
    downbeats = dbt.extract_downbeat(4,sample)
    dbt.print_and_save_downbeat(song_name, downbeats[:,0], downbeats[:,1])
    time_1, beat_num1 = downbeats[:,0].tolist(), downbeats[:,1].tolist()
    # time_1, beat_num1 = dbt.filter_downbeat(downbeats)
    # time_1 = downbeats[:,0]
    chord_dict, chord_result = dbt.get_chords_old(time_1, sample, sr)
    dbt.print_and_save_chord(song_name, downbeats[:,0], chord_result)


fullExtract(sys.argv[1])
# debugExtract(sys.argv[1])