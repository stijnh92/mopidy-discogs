from flask import Flask, render_template, request, session
import redis

from discogs import Discogs
from mopidy import Mopidy

app = Flask(__name__)
DISCOGS_API_URL = 'https://api.discogs.com/'
MOPIDY_API_URL = 'http://localhost:6680/mopidy/rpc'


@app.route('/')
def index():
    app.logger.info('getting homepage')
    return render_template('index.html')


@app.route('/user', methods=['POST'])
def user():
    username = request.form['username']
    session['username'] = username

    discogs_client = Discogs(DISCOGS_API_URL)
    discogs_client.set_user(username)

    app.logger.info('Getting folders for {}'.format(username))

    all_folders = discogs_client.get_all_folders()
    folder_ids = [folder['id'] for folder in all_folders]

    app.logger.debug('Got folders with ids {}'.format(folder_ids))

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

    app.logger.info('Getting relases for user {} for folder {}'.format(session['username'], folder_id))

    releases = discogs_client.get_folder_releases(folder_id, **parameters)

    return render_template('releases.html', releases=releases)


@app.route('/play/<title>/<artist>/<key>')
def play(title, artist, key):
    # Try to play this album on modipy
    mopidy_client = Mopidy(MOPIDY_API_URL)

    # Check if we can find a reference for this album in Redis.
    # If not, make use of the mopidy client to search.
    app.logger.debug('Trying to get {} from redis.'.format(key))
    album_uri = get_mopidy_uri(key)

    if not album_uri:
        app.logger.info('{} key not found in redis.'.format(key))

        # Let mopidy search for the title and the artist.
        album_uri = mopidy_client.search_album_from_artist(title=title, artist=artist)
        set_mopidy_uri(key, album_uri.encode('utf-8'))

    else:
        app.logger.info('{} key found in redis.'.format(key))
        album_uri = album_uri.decode('utf-8')

    if album_uri:
        # Clear the playlist
        mopidy_client.clear_tracklist()

        app.logger.info('adding uri {} to tracklist.'.format(album_uri))

        # Add the tracks of the album to the playlist.
        mopidy_client.add_album_to_tracklist(album_uri)

        # Start playing
        mopidy_client.play()

    return "playing %s - %s" % (title, artist)


def get_mopidy_uri(key):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    return r.get(key)


def set_mopidy_uri(key, value):
    r = redis.StrictRedis(host='localhost', port=6379, db=0)
    return r.set(key, value)


app.secret_key = 'MySuperSecretFlaskKeyIWillUseInProduction!'
