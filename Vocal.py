import numpy as np
import matplotlib.pyplot as plt
import librosa
import IPython.display as ipd
import librosa.display
import math
import sys

class Vocal:

    def __init__(self, file_name1, file_name2): #file_name is original, file_name2 is vocal
        self.file_name1 = file_name1
        self.file_name2 = file_name2

        self.y, sr = librosa.load(file_name1)
        self.y_D = librosa.stft(self.y)
        y_harmonic_component, y_percussive_component = librosa.decompose.hpss(self.y_D)
        y_harmonic = librosa.istft(y_harmonic_component)

        self.y_2, self.sr = librosa.load(file_name2)


        #Extract chroma
        self.chroma_1 = librosa.feature.chroma_stft(y=y_harmonic, sr=sr) 
        self.chroma_2 = librosa.feature.chroma_stft(y=self.y_2, sr=sr)
        print("Length of original", len(self.y), "Length of vocal", len(self.y_2))


    def run(self):
        self.dtw()
        self.get_offset()
        self.restretch()
        self.save()
        
    def dtw(self, isGraph=False):
        def librosa_dtw(X,Y):
            D, wp = librosa.dtw(X, Y, subseq=True)
            return D,wp
        def graph(d, wp):
            librosa.display.specshow(d, x_axis='frames', y_axis='frames')
            plt.axis('equal')
            plt.plot(wp[:, 1], wp[:, 0], label='Optimal path') #this will plot the Y as horizontal and X as vertical
        self.d, self.wp = librosa_dtw(self.chroma_2,self.chroma_1)
        if isGraph:
            graph(self.d, self.wp)

    def get_offset(self):
        test = self.wp[::-1]
        def take_mean(array):
            if len(array) == 0:
                return 0
            return sum([element[0] / element[1] for element in array]) / len(array)

        def filter_similar_slope(num_per_batch, factor, array, start, end):
            test_array = array[start:end]
            batch_num = math.ceil(len(test_array) / num_per_batch)
            mean_array = []
            print("number of bathes", batch_num, "number per batch", num_per_batch)
            for i in range(batch_num):
                mean_array.append(take_mean(test_array[i*num_per_batch :(i+1) *num_per_batch ]))
            groups = []
            new_group = []
            for i in range(1,len(mean_array)):
                if mean_array[i - 1] * factor < mean_array[i] < mean_array[i - 1] * (1 - factor + 1) :
                    new_group.append(i)
                else:
                    if len(new_group) != 0:
                        groups.append(new_group)
                        new_group = []
            if len(new_group) != 0:
                groups.append(new_group)
            return_group = max(groups, key=lambda x: len(x))
            return  start + return_group[0] * num_per_batch, start + return_group[-1] * num_per_batch

        batch1_start, batch1_end = filter_similar_slope(100, 0.99, test, 0, len(test))
        print("start_batch", batch1_start, "end_batch", batch1_end) 
        batch2_start, batch2_end = filter_similar_slope(50, 0.99, test, batch1_start, batch1_end)
        print("start_batch", batch2_start, "end_batch", batch2_end)
        batch3_start, batch3_end = filter_similar_slope(20, 0.99, test, batch2_start, batch2_end)
        print("start_batch", batch3_start, , "end_batch", batch3_end)
        # print(take_mean(test[batch3_start: batch3_end]))
        final_offset = sum(i[1] - i[0] for i in test[batch3_start: batch3_end]) // len(test[batch3_start: batch3_end])
        print(final_offset)
        self.final_offset = final_offset        

    def restretch(self):
        if self.final_offset >= 0:
            offset_frame = librosa.frames_to_samples(self.final_offset)
            noise = np.zeros(offset_frame)
            self.restretch_data = np.concatenate((noise, self.y_2), axis=0)
        else:
            offset_frame = librosa.frames_to_samples(-self.final_offset)
            # noise = np.zeros(offset_frame)        
            self.restretch_data = self.y_2[offset_frame:]

        padding = np.zeros(len(self.y) - len(self.restretch_data))
        self.final_vocal_audio = np.concatenate((self.restretch_data,padding), axis=0)

    def save(self):
        librosa.output.write_wav(self.file_name2, self.final_vocal_audio, self.sr)


Vocal(sys.argv[1], sys.argv[2]).run()