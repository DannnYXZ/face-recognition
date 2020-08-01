from sqlalchemy.orm import sessionmaker


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
    def escape_sql(x):
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
                    q_insert_images = 'INSERT INTO vk_image (vk_user_id, vk_image_type, vk_image_url, vk_image_path) VALUES ' \
                                      f"({user['id']}, 'profile', '{image['url']}', '{image['path']}')"
                    session.execute(q_insert_images)
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
