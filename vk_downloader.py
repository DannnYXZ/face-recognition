import heapq
import logging
import os
import urllib.parse as urlparse

import vk_api
from requests import get

import configuration
from mapper import map_to_user_entity


class VkDownloader:
    IMAGE_QUALITY = 0.6

    def __init__(self, login, password, user_repository):
        """
        :param login: account login
        :param password: account password
        :param user_repository: user database repository
        """
        self.vk = vk_api.VkApi(login=login, password=password, captcha_handler=self.captcha_handler)
        try:
            self.vk.auth()
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return
        self.repository = user_repository

    @staticmethod
    def captcha_handler(captcha):
        key = input('Enter captcha code {0}: '.format(captcha.get_url())).strip()
        return captcha.try_again(key)

    def add_download_task(self, user_id):
        """
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
                target_user_id = current_task[1]
                try:
                    downloaded_user = self.download_user(target_user_id)
                    downloaded_user['wave'] = current_task[0]
                    self.repository.create_user(downloaded_user)
                except Exception as e:
                    logging.log(logging.ERROR, f'Failed to download user: {target_user_id}', e)

    @staticmethod
    def download_file(url, dst_dir):
        try:
            os.makedirs(dst_dir, exist_ok=True)
        except OSError as e:
            logging.log(logging.WARN, f'Dir {dst_dir} already exists', e)
        parsed = urlparse.urlparse(url)
        local_file_path = os.path.join(dst_dir, os.path.basename(parsed.path))
        if os.path.exists(local_file_path):
            logging.log(logging.INFO, f'File {local_file_path} already exists')
            return local_file_path
        with open(local_file_path, 'wb') as file:
            response = get(url)
            file.write(response.content)
        return local_file_path

    def get_friends_ids(self, user_id):
        return self.vk.method('friends.get', {'user_id': user_id})['items']

    def download_user_images(self, user_entity):
        user_images_dir = os.path.join(configuration.DIR_IMAGES, str(user_entity['id']))
        for image in user_entity['images']:
            local_filepath = self.download_file(image['url'], user_images_dir)
            logging.log(logging.INFO, f"Downloaded image: {image['url']}")
            image['path'] = local_filepath

    def download_user(self, user_id):
        vk_user_data = self.vk.method('users.get',
                                      {
                                          'user_ids': [user_id],
                                          'fields': 'has_photo,domain,photo_max_orig,city,country,home_town,'
                                                    'can_send_friend_request,can_write_private_message,status,'
                                                    'connections,interests,sex'
                                      })[0]
        logging.log(logging.INFO, f'Fetched user data: {vk_user_data}')
        if 'deactivated' not in vk_user_data and not vk_user_data['is_closed']:
            vk_user_data['profile_images'] = self.vk.method('photos.get', {
                'owner_id': user_id,
                'album_id': 'profile'
            })['items']
            # TODO: photos.get == mentions
            vk_user_data['friends_ids'] = self.get_friends_ids(user_id)
        user_entity = map_to_user_entity(vk_user_data, self.IMAGE_QUALITY)
        self.download_user_images(user_entity)
        return user_entity

    def id_from_screen_name(self, id_or_screen_name):
        cur_response = self.vk.method('users.get', {'user_ids': {id_or_screen_name}})
        return cur_response[0]['id']
