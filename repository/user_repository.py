import os

from sqlalchemy.orm import sessionmaker

import configuration


class UserRepository:
    def __init__(self, data_source):
        self.data_source = data_source

    @staticmethod
    def get_user_images_directory(user_id):
        return os.path.join(configuration.DIR_IMAGES, str(user_id))

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
    def escape_sql(x):
        if x is None:
            return 'NULL'
        return f'\'{x}\'' if isinstance(x, str) else str(x)

    def create_user(self, user):
        """
        :param user: User object
        """
        Session = sessionmaker(bind=self.data_source)
        session = Session(bind=self.data_source)
        try:
            basic_fields = ['id', 'first_name', 'last_name', 'domain', 'is_closed', 'has_photo', 'deactivated', 'country_name',
                            'city_name', 'can_send_friend_request', 'can_write_private_message', 'interests', 'sex']
            q_insert_user = f'INSERT INTO vk_user ({", ".join(basic_fields)}) ' + \
                            f"VALUES ({', '.join([self.escape_sql(user[key]) for key in basic_fields])})"
            session.execute(q_insert_user)
            if user['images']:
                for image in user['images']:
                    q_insert_images = 'INSERT INTO image (image_type, image_url, image_path) VALUES ' \
                                      f"('profile', '{image['url']}', '{image['path']}')"
                    result = session.execute(q_insert_images)  # TODO: check
                    session.execute(f"INSERT INTO vk_user_image (vk_user_id, image_id) VALUES ({user['id']}, {result.lastrowid})")
            if user['friends_ids']:
                for friend_id in user['friends_ids']:
                    session.execute(f'INSERT INTO vk_friend (vk_user_id_from, vk_user_id_to) '
                                    f"VALUES ({user['id']}, {friend_id})")
                    session.execute(f'INSERT IGNORE INTO download_state (vk_user_id, state, wave_id) '
                                    f"VALUES ({friend_id}, {0}, {user['wave'] + 1})")
            session.execute(f"REPLACE INTO download_state (vk_user_id, state) VALUES {user['id'], 1}")
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
