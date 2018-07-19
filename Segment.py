import librosa, librosa.display, numpy
import numpy as np
import matplotlib.pyplot as plt
import IPython.display as ipd
from pprint import pprint


class Segment:

    def __init__(self, start="", end="", type=""):
        self.start = start
        self.end = end
        self.type = type
        self.downbeats = []
        self.chords = []
        self.useable = True
        self.average_time_per_beat = 0
    
    def toString(self):
        return "Start:" + str(self.start) + " End:" + str(self.end) + " Duration: " + str(self.end - self.start) + " Type:" + self.type + " downbeat_length:" + str(len(self.downbeats)) + " chord_length:" + str(len(self.chords))

    def getJSON(self):
        json_dict = dict()
        json_dict['start'] = self.start
        json_dict['end'] = self.end
        json_dict['type'] = self.type
        json_dict['downbeats'] = self.downbeats
        json_dict['chords'] = self.chords
        json_dict['useable'] = self.useable
        json_dict['average_time_per_beat'] = self.average_time_per_beat
        return json_dict

    def setJSON(self, json_dict):
        self.start = json_dict['start']
        self.end = json_dict['end']
        self.type = json_dict['type']
        self.downbeats = json_dict['downbeats']
        self.chords = json_dict['chords']
        self.useable = json_dict['useable']
        self.average_time_per_beat = json_dict['average_time_per_beat']
        return self

def extract_segment(newfile):
    result = []
    with open(newfile, 'r') as outfile:
        for line in outfile:
            if line.isspace():
                continue
            line = line.split("\t")
            result.append(Segment(float(line[0]), float(line[1]), line[2]) )
    return result
            

# print(extract_segment("segment.txt"))