

import dbt
import json
import IPython.display as ipd
import utilities 
import Segment

song1_name = "con_mua_ngang_qua_beat.wav"

import Segment
import Alignment
json_song1_name = song1_name.replace(".wav", "") + ".json"
with open(json_song1_name, "w") as json_file:
    dump_data = []
    song_data, sr  = dbt.load_and_resample(song1_name)
    song1_segments = [Segment.Segment(0, len(song_data) / sr, "")]
    for idx in range(len(song1_segments)):
        print("Loaded song_data with sr", sr, "length", len(song_data) / sr)
        print("Segment info:", song1_segments[idx].toString(), "idx", idx)    
        #Get Downbeats
        downbeats = dbt.extract_downbeat(4,song_data)
        
        time_1, beat_num1 = downbeats[:,0].tolist(), downbeats[:,1].tolist()
#         if time_1[0] > 0.07:
#             time_1 = [0.0] + time_1
#             beat_num1 = [(beat_num1[0] - 1) % 4] + beat_num1
        
        print("length time_1", len(time_1))
        #Get Chord
        chord_dict, chord_result1 = dbt.get_chords_old(time_1, song_data, sr)
        #Smoothen the chords
        print("Chord_result",chord_result1)
        new_chord_result, isAligned = Alignment.chord_alignment(chord_result1)
        song1_segments[idx].useable = isAligned
        
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
                    new_time.append(time_1[i])
            new_chord_result = new_chords
            time_1 = new_time
            
        #Average time per beat
        avg_time_beat = 0
        for i in range(len(time_1) - 1):
            avg_time_beat += time_1[i+1] - time_1[i]
        avg_time_beat = avg_time_beat / len(time_1)
        print("Average time_per_chord", avg_time_beat)
        
        if not isAligned:
            print("Cannot align chord")
        
        song1_segments[idx].chords = new_chord_result
        song1_segments[idx].downbeats = time_1
        song1_segments[idx].average_time_per_beat = avg_time_beat
        
        
        beat_num1 = [1 for i in range(len(time_1))]
        
        dbt.print_and_save_chord(song1_name, time_1, song1_segments[idx].chords, str(idx) )
        dbt.print_and_save_downbeat(song1_name, time_1, beat_num1, str(idx))
        
        dump_data.append(song1_segments[idx].getJSON())    
    json.dump(dump_data, json_file, indent=4)
        