__author__ = 'vds'

import json
import youtube_dl
import urllib.request
from urllib.parse import quote
import string

PATH = '/path/to/playlist.json'

def strip_punc(s):
    return ''.join(c for c in s if c not in string.punctuation)

with open(PATH,'r') as f:
    js = json.load(f)

songlist=[]
for song in js['tracks']['items']:
    name = strip_punc(song['track']['name'])
    artists = strip_punc(' '.join([artist['name'] for artist in song['track']['artists']]))
    songlist.append((name,artists))

YOUTUBE_API_KEY = 'AIzaSyA2NPODG9CokQzqgF457TfRCVbJb3rsV8I'

for song_tuple in songlist[1:]:
    name = song_tuple[0]
    artists = song_tuple[1]
    item = (name+' '+artists).split()
    query = quote('+'.join(item))
    req = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q=%s&key=%s' % (query,YOUTUBE_API_KEY)
    response = urllib.request.urlopen(req).read().decode('utf-8')
    results = json.loads(response)
    try:
        for yt_result in results['items']:
            title = yt_result['snippet']['title']
            if all(keyword in title for keyword in item):
                url = "https://www.youtube.com/watch?v=%s" % (yt_result['id']['videoId'])
                break
            else:
                continue
    except IndexError:
        continue
    templ = '{0} - {1}.%(ext)s'.format(artists,name)
    ydl_opts = {'quiet':True,'outtmpl':templ,'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            print(' - '.join(song_tuple),)
            ydl.download([url])
        except:
            print("Failed",query)
