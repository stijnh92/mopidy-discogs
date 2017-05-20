import requests
import urllib.parse


class Discogs(object):

    def __init__(self, base_url):
        self.base_url = base_url
        self.username = None

    def set_user(self, username):
        self.username = username

    def get_user_info(self):
        """
        [GET] /users/{username}
        Retrieve a user by username.
        """
        url = '/users/{username}'.format(username=self.username)
        result = self.get_result(url)
        if result.status_code == 200:
            return result.json()
        raise Exception('Unable to get user info for {}'.format(self.username))

    def get_all_folders(self):
        """
        [GET] /users/{username}/collection/folders
        """
        url = '/users/{username}/collection/folders'.format(
            username=self.username
        )
        result = self.get_result(url)
        if result.status_code == 200:
            return result.json()['folders']
        raise Exception('Unable to get folders for user {}'.format(self.username))

    def get_folder_info(self, folder_id):
        """
        [GET] /users/{username}/collection/folders/{folder_id}
        """
        url = '/users/{username}/collection/folders/{folder_id}'.format(
            username=self.username, folder_id=folder_id
        )
        result = self.get_result(url)
        if result.status_code == 200:
            return result.json()
        raise Exception('Unable to get folder info for folder {}'.format(
            folder_id
        ))

    def get_folder_releases(self, folder_id, **kwargs):
        """
        [GET] /users/{username}/collection/folders/{folder_id}/releases
        kwargs can be used for pagination
        """
        url = '/users/{username}/collection/folders/{folder_id}/releases'.format(
            username=self.username, folder_id=folder_id
        )
        if kwargs:
            parameters = urllib.parse.urlencode(kwargs)
            url = '{}?{}'.format(url, parameters)

        result = self.get_result(url)
        if result.status_code == 200:
            return result.json()['releases']
        raise Exception('Unable to get folder releases for folder {}'.format(
            folder_id
        ))

    def get_result(self, url, method='GET'):
        url = self.base_url + url
        if method == 'GET':
            return requests.get(url=url)
        else:
            return requests.post(url=url)
