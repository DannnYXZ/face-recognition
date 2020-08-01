import logging
import sys

from sqlalchemy import create_engine

import configuration
from repository import Repository
from vk_downloader import VkDownloader

logging.basicConfig(filename='log.log', level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

data_source = create_engine(configuration.DB_ADDRESS)
repository = Repository(data_source)
vk_downloader = VkDownloader(configuration.VK_LOGIN, configuration.VK_PASSWORD, repository)

# vk_downloader.add_download_root_task('shuntikov_foto')
# vk_downloader.add_download_root_task('danik_nikolaev')
vk_downloader.add_download_root_task('id150526316')
vk_downloader.continue_download()
# vk_downloader.download_user(vk_downloader.id_from_screen_name('shuntikov_foto'))
# vk_downloader.download_user_photos(vk_downloader.id_from_screen_name('alexgrod'))
# vk_downloader.download_file()
