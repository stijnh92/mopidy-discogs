from flask import Flask, render_template, request, session

from discogs import Discogs
from mopidy import Mopidy

app = Flask(__name__)
DISCOGS_API_URL = 'https://api.discogs.com/'
MOPIDY_API_URL = 'http://localhost:6680/mopidy/rpc'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/user', methods=['POST'])
def user():
    username = request.form['username']
    session['username'] = username

    discogs_client = Discogs(DISCOGS_API_URL)
    discogs_client.set_user(username)

    all_folders = discogs_client.get_all_folders()
    folder_ids = [folder['id'] for folder in all_folders]

    folders = {}
    # Get more information about each folder.
    for folder_id in folder_ids:
        folders.update({
            folder_id: {
                'info': discogs_client.get_folder_info(folder_id)
            }
        })

    return render_template('folders.html', folders=folders)


@app.route('/folder/<folder_id>')
def collection(folder_id):
    parameters = {
        'page': 0,
        'per_page': 1000
    }

    discogs_client = Discogs(DISCOGS_API_URL)
    discogs_client.set_user(session['username'])

    releases = discogs_client.get_folder_releases(folder_id, **parameters)

    return render_template('releases.html', releases=releases)


@app.route('/play/<title>/<artist>')
def play(title, artist):
    # Try to play this alb um on modipy
    mopidy_client = Mopidy(MOPIDY_API_URL)

    # Let mopidy search for the title and the artist.
    result = mopidy_client.search_album_from_artist(title=title, artist=artist)

    if result:
        # Clear the playlist
        mopidy_client.clear_tracklist()

        # Add the tracks of the album to the playlist.
        mopidy_client.add_album_to_tracklist(result['uri'])

        # Start playing
        mopidy_client.play()

    return "playing %s - %s" % (title, artist)


app.secret_key = 'MySuperSecretFlaskKeyIWillUseInProduction!'
