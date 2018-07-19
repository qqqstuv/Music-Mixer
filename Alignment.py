
import sys
def chord_alignment(chord_result):
    #put in chord_map {chord_name: index}, weed out N
    print(chord_result)
    chord_map = dict()
    for j in range(len(chord_result)):
        if chord_result[j] != 'N':
            if chord_result[j] not in chord_map:
                chord_map[chord_result[j]] = []
            chord_map[chord_result[j]].append(j)
    print("chord_map keys:",chord_map.keys())
    if len(chord_map) == 0:
        return chord_result, False
    #Important assumption: I assume this function works for 4 chords song so I'm going to cut the chord_map to size of 4
    if len(list(chord_map.keys())) > 4:
        sorted_length_chord_map = sorted([[len(v), k] for k,v in chord_map.items()])
        while len(chord_map) > 4:
            chord_map.pop(sorted_length_chord_map.pop(0)[1])

    # Get frequencies of int in list
    def get_freq(index_list):
        indexes_dict = dict()
        for i in index_list:
            if i not in indexes_dict:
                indexes_dict[i] = 0
            indexes_dict[i] += 1
        return indexes_dict
    
    # Return the index the chord corresponds to in the whole order and the possibility of that
    def get_quadrant(indexes_dict,beat_length):
        print(">>>>",indexes_dict,beat_length)
        size_per_bar = beat_length // 4
        indexes = sorted([[k,v] for k,v in indexes_dict.items()], key=lambda x:x[1])
        indexes = indexes[-size_per_bar:]
        indexes = [i[0] for i in indexes]
        if len(indexes_dict) < size_per_bar:
            print("WARNING: Not enough bars per chord")
        possibility = sum([indexes_dict[i] for i in indexes]) / sum (list(indexes_dict.values())) * 100
        return indexes, possibility

    Beat_lengths = [4,8,16]
    Chord_order = [
        ["" for i in range(4)],
        ["" for i in range(8)],
        ["" for i in range(16)]
    ]
    Beat_possibility = [0,0,0]

    # Detect where each chord go and the bar length of each chord
    for beat_index in range(len(Beat_lengths)):
        print("Beat_length",Beat_lengths[beat_index])
        for key,val in chord_map.items():
            total_beat_length = Beat_lengths[beat_index]
            print("key", key)
            indexes_dict = get_freq([i % total_beat_length for i in val]) # get the indexes of the chord based on the position of it in beatLength
            supposed_index, possibility = get_quadrant(indexes_dict, total_beat_length)
            for index in supposed_index:
                if Chord_order[beat_index][index] != "":
                    Beat_possibility[beat_index] = -sys.maxsize
                else:
                    Chord_order[beat_index][index] = key
            Beat_possibility[beat_index] += possibility
        print(Beat_lengths[beat_index], Beat_possibility[beat_index], Chord_order[beat_index])



    print(Beat_possibility)
    best_beat_index = Beat_possibility.index(max(Beat_possibility))
    # Reapply to chord_result
    final_chord_order = Chord_order[best_beat_index]
    final_beat_length = Beat_lengths[best_beat_index]
    print("Beat best_per_index_is", final_beat_length)
    
    # bar_per_chord = final_beat_length // 4 
    if len(final_chord_order) != final_beat_length:
        print(final_chord_order)
        print("Final_chord_order's is not ",Beat_lengths[best_beat_index])
        return chord_result, False
    
    for i in range(len(chord_result)):
        chord_result[i] = final_chord_order[i % final_beat_length]
    return chord_result, True
        

inp = ['N', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'C#:min', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'C#:min', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'C#:min', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'D:maj', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'C#:min', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'C#:min', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'D:maj', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'D:maj', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'E:maj', 'F#:min', 'D:maj', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'A:maj', 'A:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'E:maj', 'E:maj', 'F#:min', 'F#:min', 'D:maj', 'D:maj', 'A:maj', 'A:maj', 'N']        
result, alignable = chord_alignment(inp)
if alignable:
    print("Sucessfully align")
    print(result)

