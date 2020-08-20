import re

from entity_model import Face, Image
from repository.repository import Repository


class ImageMapper:
    def __init__(self, root_dir_path):
        self.root_dir_path = root_dir_path

    def remove_root_directory(self, image_path) -> str:
        return re.sub(re.escape(self.root_dir_path), '', re.escape(image_path), 1)

    def add_root_directory(self, image_path) -> str:
        return self.root_dir_path + image_path

    def map_to_image_entity(self, row_proxy):
        image = Image()
        image.id = row_proxy["image_id"]
        image.path = self.add_root_directory(row_proxy["image_path"])
        image.url = row_proxy["image_url"]
        image.type = row_proxy["image_type"]
        image.faces = []
        return image

    def map_to_image_entities(self, result_proxy):
        images = []
        for row_proxy in result_proxy:
            images.append(self.map_to_image_entity(row_proxy))
        return images


class ImageRepository(Repository):
    def __init__(self, data_source, image_mapper):
        super().__init__(data_source)
        self.image_mapper = image_mapper

    def save_image(self, image):
        q_insert_images = 'INSERT INTO image (image_type, image_url, image_path) VALUES ' \
                          f"('profile', '{image['url']}', '{self.image_mapper.remove_root_directory(image['path'])}')"
        result = self.get_connection().execute(q_insert_images)
        return result.lastrowid

    def get_image(self, image_id) -> Image:
        with self.get_connection() as connection:
            images = self.image_mapper.map_to_image_entities(
                connection.execute(f'SELECT * FROM image WHERE image_id={image_id}'))
            return images[0] if images else None

    def get_images_without_faces(self, limit: int) -> [Image]:
        """Fetches images with no faces in db"""
        with self.get_connection() as connection:
            result_proxy = connection.execute(
                f'SELECT i.* FROM image i '
                f'LEFT JOIN face f ON i.image_id = f.image_id WHERE f.id IS NULL LIMIT {limit}')
            return self.image_mapper.map_to_image_entities(result_proxy)

    def get_images_with_faces(self, faces_without_embeddings: [Face]):
        """Fetches image entities from db and adds faces to their objects"""
        with self.get_connection() as connection:
            result_proxy = connection.execute(
                f'SELECT * FROM image i LEFT JOIN face f ON i.image_id = f.image_id WHERE f.id IN ('
                f'{", ".join([str(face.id) for face in faces_without_embeddings])})')
            image_entities = self.image_mapper.map_to_image_entities(result_proxy)
            _map = {image.id: image for image in image_entities}
            for face in faces_without_embeddings:
                _map.get(face.image_id).faces.append(face)
            return image_entities
