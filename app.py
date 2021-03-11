import os
import requests
import spotipy
import time

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from helpers import apology
from googlesearch import search

#set environment variables using powershell: $env:SPOTIPY_CLIENT_ID= ""
#set FLASK_ENV to development by using: $env:FLASK_ENV="development"

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Spotify API info
CLIENT_ID = os.environ.get('CLIENT_ID')
CLIENT_SECRET = os.environ.get('CLIENT_SECRET')
REDIRECT_URI = 'http://127.0.0.1:5000/api_callback'
API_BASE = 'https://accounts.spotify.com'
SCOPE = 'playlist-modify-private, playlist-modify-public, user-top-read, user-library-read'

# Welcome page and login with Spotify
@app.route("/", methods=["GET", "POST"])
def home():
    """Display login page"""

    if request.method == "GET":
        return render_template("login.html")

    else:
        # SpotifyOAuth object that contains user token
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
        auth_url = sp_oauth.get_authorize_url()
        return redirect(auth_url)

# Request refresh and access tokens, Spotify returns access and refresh tokens
@app.route("/api_callback")
def api_callback():
    """API callback"""

    sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
    session.clear()
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code)

    # Saving the access token along with all other token related info
    session["token_info"] = token_info

    return redirect("index")

# Index page
@app.route("/index", methods=["GET", "POST"])
def index():
    """Display Index Page"""

    session['token_info'], authorized = get_token(session)
    session.modified = True
    if not authorized:
        return redirect('/')
    data = request.form
    return render_template("index.html", data=data,)

# Checks to see if token is valid and gets a new token if not
def get_token(session):
    token_valid = False
    token_info = session.get("token_info", {})

    # Checking if the session already has a token stored
    if not (session.get('token_info', False)):
        token_valid = False
        return token_info, token_valid

    # Checking if token has expired
    now = int(time.time())
    is_token_expired = session.get('token_info').get('expires_at') - now < 60

    # Refreshing token if it has expired
    if (is_token_expired):
        sp_oauth = spotipy.oauth2.SpotifyOAuth(client_id = CLIENT_ID, client_secret = CLIENT_SECRET, redirect_uri = REDIRECT_URI, scope = SCOPE)
        token_info = sp_oauth.refresh_access_token(session.get('token_info').get('refresh_token'))
    token_valid = True
    return token_info, token_valid

# Get user playlists
@app.route("/playlists", methods=["GET", "POST"])
def playlists():
    """Display User Playlists"""

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    global playlist_id, playlist_name
    playlist_id = []
    playlist_name = []
    results = sp.current_user_playlists(limit=50)
    for i in results['items']:
        playlist_id.append(i['id'])
        playlist_name = i['name']

    return render_template("playlists.html", results=results, playlist_id=playlist_id, playlist_name=playlist_name)

# Display playlist results
@app.route("/playlist_results", methods=["GET", "POST"])
def playlist_results():
    """Display Playlist Results"""
    
    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    formdata = request.form.to_dict(flat=False)
    formdata.values()

    playlist_name = formdata.keys()
    playlist_name = list(playlist_name)
    playlist_name = playlist_name[0]
    playlist_id = formdata.values()
    playlist_id = list(playlist_id)
    playlist_id = playlist_id[0][0]

    results = sp.playlist_tracks(playlist_id, fields=None, limit=40, offset=0)

    title = []
    artist = []
    query = []
    search_results = []
    search_goog = []

    for i in range(results['total']):
        title.append(results['items'][i]['track']['name'])
        artist.append(results['items'][i]['track']['artists'][0]['name'])
        query.append(title[i] + ' ' + artist[i] + ' guitar tab')
        google_search = search(query[i], num_results=0)

        if google_search == []:
            google_search = search(query[i], num_results=1)

        search_results.append(google_search)
        search_goog.append(search_results[i][0])
        if i == 39:
            break

        print(google_search)

    return render_template("playlist_results.html", playlist_id=playlist_id, playlist_name=playlist_name, search_goog=search_goog, results=results)

# Display Top Song Results
@app.route("/song_results", methods=["GET"])
def song_results():
    """Display Song Results"""

    sp = spotipy.Spotify(auth=session.get('token_info').get('access_token'))
    results = sp.current_user_top_tracks(limit=40, offset=0, time_range="long_term")

    title = []
    artist = []
    query = []
    search_results = []
    search_goog = []

    for i in range(results['total']):
        title.append(results['items'][i]['name'])
        artist.append(results['items'][i]['artists'][0]['name'])
        query.append(title[i] + ' ' + artist[i] + ' guitar tab')
        google_search = search(query[i], num_results=0)

        if google_search == []:
            google_search = search(query[i], num_results=1)

        search_results.append(google_search)
        search_goog.append(search_results[i][0])
        if i == 39:
            break
        print(google_search)

    return render_template("song_results.html", results=results, search_goog=search_goog)

if __name__ == "__main__":
    app.run(debug=True)

#Display About page
@app.route("/about")
def about():
    """Display about page"""

    return render_template("about.html")

#When user clicks on "Log out"
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session['token_info'] = ''
    session.clear()

    # Redirect user to Spotify logout page
    return redirect("http://www.spotify.com/logout")

# Return apology page with error message
def errorhandler(e):
    """Handle error"""

    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)