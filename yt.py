from __future__ import unicode_literals
import youtube_dl, sys

if len(sys.argv) > 1:
    name = sys.argv[1]
else:
    sys.exit(-1)

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}
with youtube_dl.YoutubeDL(ydl_opts) as ydl:
    ydl.download([name])
