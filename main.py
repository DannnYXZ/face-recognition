import os

from cdi import CDI

cdi = CDI()
face_detector = cdi.face_detector
face_embedder = cdi.face_embedder


def show_faces_recursive(dir_path):
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            image_path = os.path.join(root, file)
            face_detector.show_faces(image_path, face_detector.detect_faces(image_path, 0.7))


# vk_downloader = cdi.get_lazy_vk_downloader()

# vk_downloader.add_download_root_task('shuntikov_foto')
# vk_downloader.add_download_root_task('danik_nikolaev')

# vk_downloader.add_download_root_task('id150526316')
# vk_downloader.continue_download()

# vk_downloader.download_user(vk_downloader.id_from_screen_name('shuntikov_foto'))
# vk_downloader.download_user_photos(vk_downloader.id_from_screen_name('alexgrod'))
# show_faces_recursive('vk_images')

x = cdi.image_repository.get_faces_without_embeddings(1000)
y = 1
