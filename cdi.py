import logging
import sys

from sqlalchemy import create_engine

import configuration
from face_detector import FaceDetector
from face_embedder import FaceEmbedder
from repository.user_repository import UserRepository
from repository.image_repository import ImageRepository
from service.find_face_service import FindFaceService
from vk_downloader import VkDownloader


class CDI:
    def __init__(self):
        logging.basicConfig(filename='log.log', level=logging.DEBUG)
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))

        self.data_source = create_engine(configuration.DB_ADDRESS)
        self.user_repository = UserRepository(self.data_source)
        self.image_repository = ImageRepository(self.data_source)
        self.face_detector = FaceDetector(configuration.DETECTOR_PROTO_PATH, configuration.DETECTOR_WEIGHTS_PATH)
        self.face_embedder = FaceEmbedder(configuration.EMBEDDER_TORCH_MODEL_PATH)
        self.find_face_service = FindFaceService(self.image_repository, self.face_embedder, self.face_detector)

    def get_lazy_vk_downloader(self):
        return VkDownloader(configuration.VK_LOGIN, configuration.VK_PASSWORD, self.user_repository)
