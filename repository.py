import os
import shutil

from sqlalchemy.orm import Session

import configuration


class VkUser:
    def __init__(self):
        self.wave = None
        self.images = []  # {'type':, 'path':, 'url':}
        self.friends_ids = []


class Repository:
    def __init__(self, data_source):
        self.data_source = data_source

    def add_download_task(self, user_id, wave_id):
        with self.data_source.begin() as connection:
            connection.execute(
                f'INSERT IGNORE INTO download_state (vk_user_id, state, wave_id) VALUES ({user_id}, 0, {wave_id})')

    def get_users_to_download(self, limit):
        """
        :param limit: maximum users to fetch from db
        :return: array of tuples (wave_id, vk_user_id)
        """
        with self.data_source.begin() as connection:
            result_proxy = connection.execute(
                f'SELECT wave_id, vk_user_id FROM download_state WHERE state = 0 ORDER BY wave_id LIMIT {limit}')
            return [(row_proxy.items()[0][1], row_proxy.items()[1][1]) for row_proxy in result_proxy]

    @staticmethod
    def store_images(user):
        for image in user.images:
            shutil.move(image.path, os.path.join(configuration.DIR_IMAGES,
                                                 user.id,
                                                 os.path.basename(image)))

    def create_user(self, user):
        """
        :param user: User object
        """
        self.store_images(user)
        session = Session(bind=self.data_source)
        try:
            session.execute(
                'INSERT INTO vk_user '
                f'(vk_user_id, first_name, last_name, is_closed, domain, country_name, city_name, has_photo) '
                f'VALUES ({user.id}, {user.first_name}, {user.last_name}, {user.is_closed}, {user.domain}, '
                f'{user.country_name}, {user.city_name},{user.has_photo})')
            images_query = 'INSERT INTO vk_image (vk_user_id, vk_image_type, vk_image_url, vk_image_path) VALUES ' \
                           ', '.join([f'({user.id}, profile, {image.url}, {image.path})'
                                      for image in user.images])
            session.execute(images_query)
            wave_query = 'INSERT IGNORE INTO download_state (vk_user_id, state) ' \
                         ', '.join([f'({friend_id}, {user.wave + 1})' for friend_id in user.friends_ids])
            session.execute(wave_query)
        except:
            session.rollback()
            raise
        finally:
            session.close()
