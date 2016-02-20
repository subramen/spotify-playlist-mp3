#!/usr/bin/env python
__author__ = 'surajman'

import json
import youtube_dl
from urllib.parse import quote
import base64
import requests
from mutagen.easyid3 import EasyID3


YOUTUBE_API_KEY = 'AIzaSyA2NPODG9CokQzqgF457TfRCVbJb3rsV8I'
CLIENT_ID = "3692671eba56488e9123f0a607f0c36d"
CLIENT_SECRET = "650f7a04a7e0404a96d2a6e7ec11ea13"
STOPWORDS = "remastered remaster version feat featuring".split()
BLACKLIST = []        # YT results containing these words will be rejected. All lowercase only.

strip_punc = lambda s: ' '.join([word for word in s.split() if word not in STOPWORDS])



def create_tracklist(js):
# Parse Spotify playlist json for track retrieval
    songlist=[]
    for song in js['tracks']['items']:
        s={}
        s['album'] = song['track']['album']['name']
        s['album_cover'] = song['track']['album']['images'][0]['url']
        s['title'] = song['track']['name']
        s['artist'] = ', '.join([artist['name'] for artist in song['track']['artists']])
        songlist.append(s)
    return songlist



def downloader(songlist):
    
    for song in songlist:
        FOUND_FLAG = False
        
        query = (quote("{}+{}".format(song['artist'],song['title'])))
        req = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={}&key={}'.format(query,YOUTUBE_API_KEY)
        all_results = requests.get(req).json()['items']
        templ = '{0} - {1}.%(ext)s'.format(song['artist'],song['title'])
        ydl_opts = {'quiet':True,'outtmpl':templ,'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}

        print("Downloading {}".format(templ))

        for yt_result in all_results:
            title = yt_result['snippet']['title'].lower()
            meta = title+' '+yt_result['snippet']['description'].lower()

            if all(keyword in meta.split() for keyword in strip_punc((song['artist']+' '+song['title']).lower()).split()) and all(black.lower() not in title for black in BLACKLIST):
                url = "https://www.youtube.com/watch?v={}".format(yt_result['id']['videoId'])
                FOUND_FLAG = True
                break
            else:
                continue

        if not FOUND_FLAG:
            print("Not found on Youtube")
            continue


        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                print("Success")
            except:
                print("FAIL")

        tagger = EasyID3('{0} - {1}.mp3'.format(song['artist'],song['title']))
        tagger['title'] = song['title']
        tagger['artist'] = song['artist']
        tagger['album'] = song['album']
        tagger.save()



def get_access(CID, CS):
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    payload = {"grant_type" : "client_credentials"}
    base64encoded = base64.b64encode("{}:{}".format(CID,CS).encode('ascii')).decode('utf-8')
    header = {"Authorization" : "Basic {}".format(base64encoded)}
    return requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=header).json()['access_token']


def ui():
    url = input("Spotify playlist URI: (E.g: spotify:user:spotify:playlist:2kW7mAXQD59R08Sz6RJizo)\n")
    
    if url.startswith('spotify:'):
        url = url.split(sep=':')
        user = url[2]
        plid = url[4]
    elif url.startswith('http://'):
        url = url.split(sep='/')
        user = url[4]
        plid = url[6]
    else:
        print('Invalid URL.')
        quit()

    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    payload = {"grant_type" : "client_credentials"}
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID,CLIENT_SECRET).encode('ascii')).decode('utf-8')
    header = {"Authorization" : "Basic {}".format(base64encoded)}
    spotify_oauth = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=header).json()['access_token']

    url = "https://api.spotify.com/v1/users/{}/playlists/{}?fields=name,tracks.items(track(name,artists,album))".format(user,plid)
    header = {"Authorization" : "Bearer {}".format(spotify_oauth)}
    return requests.get(url, headers=header).json()


def main():
    pl = ui()
    songlist = create_tracklist(pl)  # List of songs in the playlist
    for c,song in enumerate(songlist): # Display all songs in playlist
        print('{0}  {1} - {2}'.format(c,song['artist'],song['title']))
    try:
        dnd = [int(x) for x in input("Enter comma-separated numbers of those tracks you DON'T want to download (-> 1,3,5)\n-> ").split(sep=',')]
        songlist = [song for c,song in enumerate(songlist) if c not in dnd]
    except ValueError:
        pass
    downloader(songlist)

if __name__ == "__main__":
    main()





