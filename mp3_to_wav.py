
from pydub import AudioSegment
import sys

input_path = sys.argv[1]
output_path = input_path.strip("mp3")
output_path += "wav"
sound = AudioSegment.from_mp3(input_path)
sound.export(output_path, format="wav")