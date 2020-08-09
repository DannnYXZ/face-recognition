import os

import cv2
import imutils

import configuration
from cdi import CDI
from face_detector import FaceDetector
from face_embedder import FaceEmbedder


def show_faces_recursive(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            image_path = os.path.join(root, file)
            face_detector.show_faces(image_path, face_detector.detect_faces(image_path, 0.7))


cdi = CDI()
# vk_downloader = cdi.get_lazy_vk_downloader()

# vk_downloader.add_download_root_task('shuntikov_foto')
# vk_downloader.add_download_root_task('danik_nikolaev')

# vk_downloader.add_download_root_task('id150526316')
# vk_downloader.continue_download()

# vk_downloader.download_user(vk_downloader.id_from_screen_name('shuntikov_foto'))
# vk_downloader.download_user_photos(vk_downloader.id_from_screen_name('alexgrod'))

face_detector = FaceDetector(configuration.DETECTOR_PROTO_PATH, configuration.DETECTOR_WEIGHTS_PATH)
face_embedder = FaceEmbedder(configuration.EMBEDDER_TORCH_MODEL_PATH)

image = cv2.imread('break.jpg')
print(face_embedder.extract_embedding(image, face_detector.detect_faces(image, .7)[0][:4]))

# show_faces_recursive('vk_images')
