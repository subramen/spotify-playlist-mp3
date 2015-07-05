# spotify-playlist-mp3
Retrieves the track listing in any Spotify playlist and rips the mp3 from YouTube.

Requires: youtube_dl,
          Spotify account

Spotify provides all playlist data in a JSON response. To GET it, an OAuth token is required. I am generating a token in their API Console - https://developer.spotify.com/web-api/console/get-playlist/ - and downloading the response to disk. The script uses the JSON file obtained from the console. 



