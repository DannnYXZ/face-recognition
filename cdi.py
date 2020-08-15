import logging
import sys

from sqlalchemy import create_engine

import configuration
from repository.user_repository import UserRepository
from repository.image_repository import ImageRepository
from vk_downloader import VkDownloader


class CDI:
    def __init__(self):
        logging.basicConfig(filename='log.log', level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        self.data_source = create_engine(configuration.DB_ADDRESS)
        self.user_repository = UserRepository(self.data_source)
        self.image_repository = ImageRepository(self.data_source)

    def get_lazy_vk_downloader(self):
        return VkDownloader(configuration.VK_LOGIN, configuration.VK_PASSWORD, self.user_repository)
