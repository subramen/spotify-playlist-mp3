import youtube_dl
from urllib.parse import quote
import string
import base64
import requests

# Enter your Client ID and Secret. Go to https://developer.spotify.com/my-applications/#!/applications.
CLIENT_ID = ""
CLIENT_SECRET = ""
BLACKLIST = ['live']        # YT results containing these words will be rejected. All lowercase only.


def strip_punc(s):
    return ''.join(c for c in s if c not in string.punctuation)

def create_tracklist(js):
# Pass the Spotify playlist json for track retrieval
    songlist=[]
    for song in js['tracks']['items']:
        name = strip_punc(song['track']['name'])
        artists = strip_punc(' '.join([artist['name'] for artist in song['track']['artists']]))
        songlist.append((artists,name))
    return songlist

def downloader(songlist):
    YOUTUBE_API_KEY = 'AIzaSyA2NPODG9CokQzqgF457TfRCVbJb3rsV8I'
    for song_tuple in songlist:
        artists = song_tuple[0]
        name = song_tuple[1]
        item = (name+' '+artists).split()
        query = quote('+'.join(item))
        req = 'https://www.googleapis.com/youtube/v3/search?part=snippet&type=video&q={}&key={}'.format(query,YOUTUBE_API_KEY)
        all_results = requests.get(req).json()['items']
        found_flag = False
        templ = '{0} - {1}.%(ext)s'.format(artists,name)
        ydl_opts = {'quiet':True,'outtmpl':templ,'format': 'bestaudio/best','postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}]}

        for yt_result in all_results:
            title = strip_punc(yt_result['snippet']['title']).lower()
            if all(keyword.lower() in title for keyword in item) and all(black.lower() not in title for black in BLACKLIST):
                url = "https://www.youtube.com/watch?v={}".format(yt_result['id']['videoId'])
                found_flag = True
                break
            else:
                continue
        print(' - '.join(song_tuple),end='  ...  ')
        if not found_flag:
            print("Not found on Youtube")
            continue
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            try:
                ydl.download([url])
                print("Success")
            except:
                print("FAIL")


def get_access(CID, CS):
    SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
    payload = {"grant_type" : "client_credentials"}
    base64encoded = base64.b64encode("{}:{}".format(CID,CS).encode('ascii')).decode('utf-8')
    header = {"Authorization" : "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=payload, headers=header)
    response = post_request.json()
    access_token = response['access_token']
    return access_token

def get_playlist(user,plid):
    spotify_oauth = get_access(CLIENT_ID,CLIENT_SECRET)
    url = "https://api.spotify.com/v1/users/{}/playlists/{}?fields=name,tracks.items(track(name,artists))".format(user,plid)
    header = {"Authorization" : "Bearer {}".format(spotify_oauth)}
    get_request = requests.get(url, headers=header)
    response = get_request.json()
    return response

def ui():
    url = input("Spotify playlist URI:\n").split(sep=':')
    # E.g: spotify:user:spotify:playlist:2kW7mAXQD59R08Sz6RJizo
    user = url[2]
    plid = url[4]
    pl = get_playlist(user,plid) # Dict of playlist json
    songlist = create_tracklist(pl)  # List of songs in the playlist
    for c,song in enumerate(songlist): # Display all songs in playlist
        print('{0}  {1}'.format(c,' - '.join(song)))
    try:
        dnd = [int(x) for x in input("Enter comma-separated numbers of those tracks you DON'T want to download (-> 1,3,5)\n-> ").split(sep=',')]
        songlist = [song for c,song in enumerate(songlist) if c not in dnd]
    except ValueError:
        pass
    downloader(songlist)

if __name__ == "__main__":
    ui()





