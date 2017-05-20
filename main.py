import random

from discogs import Discogs
from mopidy import Mopidy


DISCOGS_API_URL = 'https://api.discogs.com/'
DISCOGS_USER = 'stijnh92'

MOPIDY_API_URL = 'http://localhost:6680/mopidy/rpc'


def get_public_collection():
    # Create new Discogs client instance with the discogs API url.
    discogs_client = Discogs(DISCOGS_API_URL)

    # Set the user we want to get the data from.
    discogs_client.set_user(DISCOGS_USER)
    user_info = discogs_client.get_user_info()
    print("Getting information for {}".format(user_info['name']))

    # Get all the public folders from this user.
    # TODO: Implement authentication so we can get all the folders.
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

    # Get the releases for this user for each folder
    for folder_id, folder in folders.items():
        # TODO: Implement some sort of pagination.
        parameters = {
            'page': 0,
            'per_page': folder['info']['count']
        }
        releases = discogs_client.get_folder_releases(folder_id, **parameters)
        folders[folder_id].update({
            'releases': releases
        })

    print('Successfully retrieved releases from {}'.format(DISCOGS_USER))
    return folders


def play_album():
    print('Playing {} by {} ...'.format(title, artist))
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

if __name__ == '__main__':
    collection = get_public_collection()

    # Start playing some random album from this collection
    collection_size = collection[0]['info']['count']

    random_nr = random.randint(0, collection_size) - 1
    album = collection[0]['releases'][random_nr]['basic_information']

    artist = album['artists'][0]['name']
    title = album['title']

    play_album()
