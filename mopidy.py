import json
import requests


class Mopidy(object):

    def __init__(self, base_url):
        self.base_url = base_url

    def search_album_from_artist(self, title, artist):
        data = {
            'params': {
                'query': {
                    'artist': [artist],
                    'album': [title]
                },
                'uris': None,
                'exact': True
            },
        }

        method = 'core.library.search'
        result = self.post(method, data).json()['result'][0]

        if 'albums' in result:
            return result['albums'][0]
        raise Exception('{} by {} not found on Mopidy!'.format(title, artist))

    def clear_tracklist(self):
        # Clear tracklist
        method = 'core.tracklist.clear'
        self.post(method, {})

    def add_album_to_tracklist(self, album_uri):
        method = 'core.tracklist.add'
        data = {
            'params': {
                'uri': album_uri,
            },
        }
        self.post(method, data)

    def play(self):
        method = 'core.playback.play'
        self.post(method, {})

    def post(self, method, values):
        data = {
            'jsonrpc': '2.0',
            'id': 1,
            'method': method
        }
        data.update(values)
        return requests.post(url=self.base_url, data=json.dumps(data))
