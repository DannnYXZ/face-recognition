import heapq
import os
import urllib.parse as urlparse
import uuid

from requests import get

import vk_api

import configuration
from mapper import map_to_vk_user
from repository import VkUser


class VkDownloader:
    def __init__(self, login, password, repository):
        """
        :param login: account login
        :param password: account password
        :param repository: database repository
        """
        self.vk = vk_api.VkApi(login=login, password=password, captcha_handler=self.captcha_handler)
        try:
            self.vk.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return
        self.repository = repository

    @staticmethod
    def captcha_handler(captcha):
        key = input('Enter captcha code {0}: '.format(captcha.get_url())).strip()
        return captcha.try_again(key)

    def add_download_root_task(self, user_id):
        """
        :param wave_id: BFS front wave id
        :param user_id: id or screen name
        """
        self.repository.add_download_task(self.id_from_screen_name(user_id), 1)

    def get_users_to_download(self, limit):
        return self.repository.get_users_to_download(limit)

    def continue_download(self):
        """
        Continue load social network to local database
        """
        while True:
            download_tasks = self.get_users_to_download(100)
            if not download_tasks:
                break
            heapq.heapify(download_tasks)
            first_task = download_tasks[0]
            while download_tasks:
                current_task = heapq.heappop(download_tasks)
                if current_task[0] != first_task[0]:
                    break
                downloaded_user = self.download_user(current_task[1])
                downloaded_user.wave = current_task[0]
                self.repository.create_user(downloaded_user)

    @staticmethod
    def download_file(url):
        parsed = urlparse.urlparse(url)
        local_filename = os.path.join(configuration.DIR_IMAGES, str(uuid.uuid1()) + os.path.splitext(parsed.path)[1])
        with open(local_filename, 'wb') as file:
            response = get(url)
            file.write(response.content)
        return local_filename

    def get_friends_ids(self, user_id):
        return self.vk.method('friends.get', {'user_id': user_id})['items']

    def download_user(self, user_id):
        vk_user_data = self.vk.method('users.get',
                                      {
                                          'user_ids': [user_id],
                                          'fields': 'has_photo,domain,photo_max_orig,city,country'
                                      })[0]
        user = map_to_vk_user(vk_user_data)
        # TODO: photos.get == mentions
        print(vk_user_data)
        if vk_user_data['has_photo']:
            local_filepath = self.download_file(vk_user_data['photo_max_orig'])
            user.images.append({'type': 'profile', 'path': local_filepath, 'url': vk_user_data['photo_max_orig']})
        if not vk_user_data['is_closed']:
            profile_photos = self.vk.method('photos.get', {
                'owner_id': user_id,
                'album_id': 'profile'
            })['items']
            for image in profile_photos:
                original_image = image['sizes'][-1]
                print(original_image)
                local_filepath = self.download_file(original_image['url'])
                user.images.append({'type': 'profile', 'path': local_filepath, 'url': original_image['url']})
            user.fiends_ids = self.get_friends_ids(user_id)
        return user

    def id_from_screen_name(self, screen_name):
        cur_response = self.vk.method('users.get', {'user_ids': {screen_name}})
        return cur_response[0]['id']
