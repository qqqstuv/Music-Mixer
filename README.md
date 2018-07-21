# Music-Mixer

### Update on May 7, 2018

- I tried to mix Just a Dream by Nelly with If I were a boy by Beyonce on Adobe Audition. I downloaded the vocal for Just a Dream and the backing track for If I were a boy and just align them together. Since they have the same tempo and the same chords, it turns out to be pretty good. 
- I tried mixing Love the way you lie with If I were a boy but there is a pause in the first song which makes everything out of sync without editing
- I also tried to mix River Flows in you and Just A Dream with pitch -3 on River flows in you. It sounded great!
- I feel like I need to detect the following:
  + tempo
  + where the chord begins
  + chord transposition for songs that have the same chords but at different transposition
  
- At this point, I think I have the following approaches:
  + get vocals and focus on extracting the tempo, the chord and timing and form a database of that
  + get backing track and detect possible parts to add the vocals in.
  + I can just use backing track of EDM songs, classical music, dubstep music, catchy piano tunes and does not neccessarily have to be backtrack from pop songs.
  + It would be good if I can do chorus, first/second lyrics detections and just apply that to specific time frame
  
- Steps to be done to mix 2 songs:
1. Detect the tempo
2. Detect where to match

- Case of Havana and Smooth: the chords don't match exactly but it still works magically.


#### Update on May 10, 2018
- Things to ask:
  + Dynamic Time Wrapping and how I can use it to synchronize two songs.
  + How to stretch a song based on tempo and to how cut songs in the right way.

#### Update on July 15, 2018
- Finally made some progress
- Ditched DTW approach
- Things to do:
  Figure out how many bars each chord has (Solved this my making an algorithm that detect chord automatically)
  How to deal with songs that have the 7 chord (Cant)
  Can I mash songs with the same chord but different order? Possible wrong match
  How about songs that can generate random chords
  Sometimes I have divide by zero problem in numpy seemingly from librosa. How do I fix it?
  Maybe only do different parts in segments?
  

#### Update on July 17, 2018  
- Things can do:
  Predict the final chord in the list
  Group Similar processed chords together along with timestamp (Done)
  Go to Alignment and fix the error sometimes it detect the wrong major/minor(For the 3rd part in just a dream)
  Sometimes it detects the wrong shift because it assumes that the new bar starts at index 0 but the segment may be off


#### Update on July 18, 2018
- I think I have implemented a stable version of aligning chords given chords and beats 
- I stop trying the segmentation for now.
- Make sure spectral balance (low and high). High pass fitler, low pass filter

#### Update on July 19, 2018
C  Dm Em F  G  Am Bdim
1  2  3  4  5  6  7
- Some important distinction between the song order: C: 1, Am: 6, F: 4, G: 5
  + “Just a Dream” Nelly 6-4-1-5
  + "Crying" Aerosmith: 1-5-6-4
  + "So Sick" Neyo 6-4-1-5

- Maybe extract the song partially and only try to merge part of it. 
- Song that have different ending/ different chord at the end


#### Update on July 20,2018
- Got a somewhat stable version working. Failed on "Con Mua Ngang Qua".
- Maybe extract partially matching part of each chord.
- TODO: optimize runtime in dbt
- TODO: Adjust spectral balance in the final step

#### Update on July 21, 2018
- Need to fix audio produce no sound on give_your_heart_a_break and pay_phone
- So Sick doesn't work