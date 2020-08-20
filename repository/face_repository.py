import json

import numpy as np

from entity_model import Face
from repository.repository import Repository


class FaceMapper:
    @staticmethod
    def map_to_face_entity(row_proxy):
        face = Face()
        face.id = row_proxy["id"]
        face.image_id = row_proxy["image_id"]
        face.start_x = row_proxy["start_x"]
        face.start_y = row_proxy["start_y"]
        face.end_x = row_proxy["end_x"]
        face.end_y = row_proxy["end_y"]
        face.confidence = row_proxy["confidence"]
        face.embedding = np.array(json.load(row_proxy["embedding"])) if row_proxy["embedding"] else None
        return face

    @staticmethod
    def map_to_face_entities(result_proxy):
        faces = []
        for row_proxy in result_proxy:
            faces.append(FaceMapper.map_to_face_entity(row_proxy))
        return faces


class FaceRepository(Repository):
    def __init__(self, data_source):
        super().__init__(data_source)

    def save_face_regions(self, image_id, detections):
        with self.get_connection() as connection:
            for detection in detections:
                connection.execute(
                    f"INSERT INTO face (image_id, start_x, start_y, end_x, end_y, confidence) "
                    f"VALUES ({image_id}, {', '.join(map(str, detection))})")

    def save_face_embedding(self, face_id, embedding: str):
        with self.get_connection() as connection:
            str_embedding = json.dumps(embedding.tolist()) if embedding is not None else 'NULL'
            connection.execute(f"UPDATE face SET embedding = '{str_embedding}' WHERE id={face_id}")

    def get_faces_without_embeddings(self, limit: int) -> [Face]:
        with self.get_connection() as connection:
            result_proxy = connection.execute(f'SELECT * FROM face i WHERE embedding IS NULL LIMIT {limit}')
            return FaceMapper.map_to_face_entities(result_proxy)
