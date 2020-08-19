import os
import cv2
from repository.user_repository import UserRepository
from cdi import CDI

cdi = CDI()
face_detector = cdi.face_detector
face_embedder = cdi.face_embedder


def show_faces_recursive(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            image_path = os.path.join(root, file)
            face_detector.show_faces(image_path, face_detector.detect_faces(image_path, 0.7))


def download():
    vk_downloader = cdi.get_lazy_vk_downloader()
    vk_downloader.add_download_task('id150526316')
    vk_downloader.continue_download()


# download()
# vk_downloader.add_download_root_task('shuntikov_foto')
# vk_downloader.add_download_root_task('danik_nikolaev')


# vk_downloader.download_user(vk_downloader.id_from_screen_name('shuntikov_foto'))
# vk_downloader.download_user_photos(vk_downloader.id_from_screen_name('alexgrod'))
# show_faces_recursive('vk_images')

image_entity = cdi.image_repository.get_image(2118)
image = cv2.imread(os.path.join(UserRepository.get_user_images_directory(user_id=16737748), image_entity.path))
x = cdi.image_repository.save_face_regions(2118, cdi.face_detector.detect_faces(image, 0.7))
y = 1
