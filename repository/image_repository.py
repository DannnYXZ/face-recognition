from entity_model import Face, Image
from mapper import map_to_image_entities


class ImageRepository:
    def __init__(self, data_source):
        self.data_source = data_source

    def get_image(self, image_id) -> Image:
        with self.data_source.begin() as connection:
            images = map_to_image_entities(connection.execute(f'SELECT * FROM image WHERE image_id={image_id}'))
            return images[0] if images else None

    def get_faces_without_embeddings(self, limit: int) -> [Face]:
        with self.data_source.begin() as connection:
            result_proxy = connection.execute(f'SELECT * FROM face i WHERE embedding IS NULL LIMIT {limit}')
            return map_to_image_entities(result_proxy)

    def get_images_without_faces(self, limit: int) -> [Image]:
        """Fetches images with no faces in db"""
        with self.data_source.begin() as connection:
            result_proxy = connection.execute(
                f'SELECT i.* FROM image i '
                f'LEFT JOIN face f ON i.image_id = f.image_id WHERE f.id IS NULL LIMIT {limit}')
            return map_to_image_entities(result_proxy)

    def get_images_with_faces(self, faces_without_embeddings: [Face]):
        """Fetches image entities from db and adds faces to their objects"""
        with self.data_source.begin() as connection:
            result_proxy = connection.execute(
                f'SELECT * FROM image i LEFT JOIN face f ON i.image_id = f.image_id WHERE f.id IN ('
                f'{", ".join([face.id for face in faces_without_embeddings])})')
            image_entities = map_to_image_entities(result_proxy)
            _map = {image.id: image for image in image_entities}
            for face in faces_without_embeddings:
                _map.get(face.image_id).faces.append(face)

    def save_face_regions(self, image_id, detections):
        with self.data_source.begin() as connection:
            for detection in detections:
                connection.execute(
                    f"INSERT INTO face (image_id, start_x, start_y, end_x, end_y, confidence) "
                    f"VALUES ({image_id}, {', '.join(map(str, detection))})")

    def save_face_embedding(self, face_id, embedding: str):
        with self.data_source.begin() as connection:
            connection.execute(f"UPDATE face SET embedding = {embedding} WHERE id={face_id}")
