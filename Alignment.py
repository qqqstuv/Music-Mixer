
import sys
import numpy as np
import matplotlib.pyplot as plt

def plot(plot_key_dict, beat_length):
    print("DATA", plot_key_dict)
    n_groups = beat_length
    index = np.arange(n_groups)
    print("INDEX",index)
    fig, ax = plt.subplots()
    
    bar_width = 0.5

    opacity = 1
    error_config = {'ecolor': '0.3'}

    colors = ['black', 'green','firebrick','gold']
    color_i = 0
    for key in list(plot_key_dict.keys()):
        data = [0 for i in range(beat_length)]
        for i, val in plot_key_dict[key].items():
            data[i] = val
        rect = plt.bar(index + bar_width * color_i / 4, data, bar_width / 4,
                        alpha=opacity,
                        color=colors[color_i],
                        # yerr=std_men,
                        error_kw=error_config,
                        label=key)
        color_i += 1
    plt.xlabel('BEAT')
    plt.ylabel('COUNT')
    plt.title('Scores by chord and beat frequencies')
    print("index",index)
    plt.xticks(index + bar_width/3, [i for i in range(beat_length)]   )
    plt.legend()
    plt.savefig("temp_" + str(beat_length) +".png")
    plt.tight_layout()
    # plt.show()

def chord_alignment(chord_result):
    #put in chord_map {chord_name: index}, weed out N
    # print(chord_result)
    chord_map = dict()
    for j in range(len(chord_result)):
        if chord_result[j] != 'N':
            if chord_result[j] not in chord_map:
                chord_map[chord_result[j]] = []
            chord_map[chord_result[j]].append(j)
    for key,val in chord_map.items():
        print("Key",key,"# of instances", len(val))
    if len(chord_map) == 0:
        return chord_result, False
    #Important assumption: I assume this function works for 4 chords song so I'm going to cut the chord_map to size of 4
    if len(list(chord_map.keys())) > 4:
        sorted_length_chord_map = sorted([[len(v), k] for k,v in chord_map.items()])
        while len(chord_map) > 4:
            chord_map.pop(sorted_length_chord_map.pop(0)[1])
    print("chord_map keys:",chord_map.keys())


    # Get frequencies of int in list
    def get_freq(index_list):
        indexes_dict = dict()
        for i in index_list:
            if i not in indexes_dict:
                indexes_dict[i] = 0
            indexes_dict[i] += 1
        return indexes_dict
    
    # Return the index the chord corresponds to in the whole order and the possibility of that
    # def get_quadrant(indexes_dict,beat_length):
    #     print(">>>>",indexes_dict)
    #     size_per_bar = beat_length // 4
    #     indexes = sorted([[k,v] for k,v in indexes_dict.items()], key=lambda x:x[1])
    #     indexes = indexes[-size_per_bar:]
    #     indexes = [i[0] for i in indexes]
    #     if len(indexes_dict) < size_per_bar:
    #         print("WARNING: Not enough bars per chord")
    #     possibility = sum([indexes_dict[i] for i in indexes]) / sum (list(indexes_dict.values())) * 100
    #     return indexes, possibility

    def get_quadrant(chord_freq, beat_length):

        # Create and array and pad with 0 for index without chord frequencies

        padded_chord_freq = dict() 
        for k,v in chord_freq.items():
            activation_list = [0 for i in range(beat_length)]
            for _index, _frequency in chord_freq[k].items():
                activation_list[_index] = _frequency
            padded_chord_freq[k] = activation_list
        chord_freq = padded_chord_freq

        for _k, _v in chord_freq.items():
            print('chord_freq', _k,_v)

        def transform(input_chord, total_bar_length, shift_amount): # group frequencies based on length of each bar
            new_input_dict = dict()
            for key in list(input_chord.keys()):
                new_val = []
                for i in range(len(input_chord[key])):
                    if i % (total_bar_length // 4) == shift_amount:  # each total_bar_length // 4, or 1,2,4 bars per chord
                        total_sum = 0
                        for j in range(total_bar_length // 4):
                            total_sum += input_chord[key][(i + j) % total_bar_length]
                        new_val.append(total_sum)
                new_input_dict[key] = new_val
            return new_input_dict

        shift_times = beat_length // 4
        final_transformed_tuple = [] # contain the order and the percentage of correct
        for shift_time in range(shift_times):
            new_input_dict = transform(chord_freq, beat_length, shift_time)
            print("new_input_dict", new_input_dict)
            predicted_chord_order = { k: v.index(max(v))  for k,v in new_input_dict.items()}
            if set([i for i in range(4)]) != set(predicted_chord_order.values()):
                print("Failed to align")
            else:
                possibility = sum([ new_input_dict[key][val] / sum(new_input_dict[key]) for key,val in list(predicted_chord_order.items())])
                final_transformed_tuple.append([predicted_chord_order,possibility,shift_time ])
        print(final_transformed_tuple)
        if final_transformed_tuple:
            return max(final_transformed_tuple, key=lambda x: x[1])
            # return final_transformed_tuple[3]
        else:
            return [{}, -sys.maxsize, 0]

    Beat_lengths = [4,8,16]
    Chord_order = [
        ["" for i in range(4)],
        ["" for i in range(8)],
        ["" for i in range(16)]
    ]
    Beat_possibility = [0,0,0]
    Beat_shift = [0,0,0]
    

    # Detect where each chord go and the bar length of each chord

    for beat_index in range(len(Beat_lengths)):
        print("Beat_length",Beat_lengths[beat_index])
        input_chord = dict()
        
        for key,val in chord_map.items():
            total_beat_length = Beat_lengths[beat_index]
            print("Key", key)
            indexes_dict = get_freq([i % total_beat_length for i in val]) # get the indexes of the chord based on the position of it in beatLength
            input_chord[key] = indexes_dict
        beat_order, possibility, shift = get_quadrant(input_chord, total_beat_length)
        Beat_possibility[beat_index] += possibility
        Chord_order[beat_index] = beat_order
        Beat_shift[beat_index] = shift

    print(Beat_possibility)
    best_beat_index = Beat_possibility.index(max(Beat_possibility))
    # Reapply to chord_result
    final_chord_order = Chord_order[best_beat_index]
    final_beat_length = Beat_lengths[best_beat_index]
    final_beat_shift = Beat_shift[best_beat_index]
    print("Beat best_per_index_is", final_beat_length)
    print("Beat final_chord_order", final_chord_order)
    print("Beat final_beat_shift", final_beat_shift)
    reversed_chord_order = {v: k for k, v in final_chord_order.items()}
    
    # bar_per_chord = final_beat_length // 4 
    # if len(final_chord_order) != final_beat_length // 4:
    #     print(final_chord_order)
    #     print("Final_chord_order's is not ",Beat_lengths[best_beat_index])
    #     return chord_result, False
    
    for i in range(len(chord_result)):
        # print(chord_result[i], reversed_chord_order[((i - 1) % final_beat_length) // (final_beat_length // 4)])
        chord_result[i] = reversed_chord_order[((i - final_beat_shift) % final_beat_length) // (final_beat_length // 4)]
        # chord_result[i] = reversed_chord_order[  ((i % final_beat_length) // (final_beat_length // 4) ) % 4 + final_beat_shift]
        # print(chord_result[i])
    return chord_result, True
        

# inp  =['D#:min', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'N', 'N', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'N', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'F#:maj', 'F#:maj', 'G#:maj', 'G#:min', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'G#:maj', 'N', 'B:maj', 'B:maj', 'D#:min', 'F#:maj', 'C#:maj', 'C#:maj', 'G#:min', 'G#:min', 'B:maj', 'B:maj', 'D#:min', 'F#:maj', 'C#:maj', 'C#:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'D#:min', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'D#:min', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'D#:min', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'D#:min', 'F#:maj', 'B:maj', 'B:maj', 'F#:maj', 'F#:maj', 'C#:maj', 'C#:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'B:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:min', 'N', 'B:maj', 'N', 'F#:maj', 'C#:maj']
# inp = ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'G:min', 'D#:maj', 'D#:maj', 'D#:maj', 'D#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'N', 'F:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'C:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'C:maj', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'N', 'N', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'D#:maj', 'C:min', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'G:min', 'N', 'C:maj', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'C:min', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'F:maj', 'N', 'F:maj', 'N', 'G:min', 'N', 'C:maj', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'N', 'N', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'F:maj', 'N', 'N', 'N', 'C:maj', 'N', 'D#:maj', 'D#:maj', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'D#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'G:min', 'D#:maj', 'D#:maj', 'C:min', 'D#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'D#:maj', 'A#:maj', 'N', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'N', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'N', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'D#:maj', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']
# inp2 = ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'G:min', 'D#:maj', 'D#:maj', 'D#:maj', 'D#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'N', 'F:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'C:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'C:maj', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'N', 'N', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'D#:maj', 'C:min', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'G:min', 'N', 'C:maj', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'C:min', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'F:maj', 'N', 'F:maj', 'N', 'G:min', 'N', 'C:maj', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'N', 'N', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'F:maj', 'N', 'N', 'N', 'C:maj', 'N', 'D#:maj', 'D#:maj', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'D#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'G:min', 'D#:maj', 'D#:maj', 'C:min', 'D#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'D#:maj', 'A#:maj', 'N', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'F:maj', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'A#:maj', 'N', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'A#:maj', 'N', 'N', 'A#:maj', 'N', 'N', 'N', 'N', 'G:min', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'A#:maj', 'N', 'A#:maj', 'A#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'D#:maj', 'D#:maj', 'N', 'N', 'A#:maj', 'A#:maj', 'A#:maj', 'A#:maj', 'F:maj', 'F:maj', 'F:maj', 'F:maj', 'N', 'N', 'N', 'N', 'D#:maj', 'N', 'N', 'N', 'N', 'N', 'N', 'N', 'N']

# result, alignable = chord_alignment(inp)
# if alignable:
#     print("Sucessfully align")
#     # print(result)

# # print(inp2[:20])
# # print(inp[:20])
# count_wrong = 0
# for i in zip(inp2, inp[4:]):
#     if i[0] != 'N' and i[0] == i[1]:
#         count_wrong += 1
#         # print(">",i[0], i[1])

#     # print(i)
# print(count_wrong, len(inp2))

# count_right = 0
# for i in zip(inp2, inp):
#     if i[0] != 'N' and i[0] == i[1]:
#         count_right += 1
#         # print(">",i[0], i[1])
# print(count_right, len(inp2))


# for i in zip(inp2, inp):
#     print(">",i[0], i[1])



