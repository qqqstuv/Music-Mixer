# Music-Mixer

My music mixer project that I did during the summer of 2018, directed by Dr. George Tzanetakis.

## Objective:
To create a software that automatically mixes two songs together

### Project Scope;
- Songs with four chords: Am, F, C, G
- Constant beats, 4/4 Time Signature
- No changes in time.

## Overview

![alt text](https://github.com/dukeng/Music-Mixer/blob/master/overview.png "Logo Title Text 1")

## How to run

### To extract a song:
```python
python Extract.py <song_name.wav>
```

### To match the song with its vocal:
```python
python Vocal.py <song_name.wav> <vocal_name.wav> 
```

### To create a mashup:
```python
python Reassemble.py <beat_name.wav> <vocal_name.wav> 
```

