# Tablify

#### Video demonstration of Tablify here: YOUTUBE LINK

## Description

#### Tablify is a web app that reads your Spotify playlists and top played songs and returns links to guitar tabs for each song.
#### The web app requires you to login with your Spotify account (free accounts are okay) and then uses the Spotify API in order to read your saved playlists and your top played tracks (both limited to 50 songs). Once you select from one of your playlists or top songs you are then taken to a page that displays the selected songs and a guitar link to that song (if the tab exists!).

#### The web app was written in python using the Flask framework. The dynamic web app utilises the Jinja2 web template engine to inject user elements into the web pages such as user playlists, tracks, artists and albums. User authentication in the Spotify API was done using the Authorization Code Flow as detailed in the Spotify Developer documentation: https://developer.spotify.com/documentation/general/guides/authorization-guide/. 

## How To Run Locally

#### Clone repo
#### `$ git clone https://github.com/duncanhmurray9/Tablify.git`

#### Set environment variables in order to use Flask
#### `$env:FLASK_ENV="development"`

#### Sign up for a Spotify development account (using your existing Spotify acount) at: `https://developer.spotify.com/dashboard`, and obtain your Client ID and Client Secret.

#### On the Spotify dashboard, go to edit settings and add `http://127.0.0.1:5000/api_callback` as the Redirect URI.

#### Set environment variables of Client ID and Client Secret
#### `$env:CLIENT_ID = "YOUR CLIENT ID HERE"`
#### `$env:CLIENT_SECRET = "YOUR CLIENT SECRET HERE"`

#### Restart your IDE so that it recognises the environment variables.

#### Execute flask in terminal
#### `flask run`

#### CTRL click `http://127.0.0.1:5000/` in the terminal to open the web app in your default browser.