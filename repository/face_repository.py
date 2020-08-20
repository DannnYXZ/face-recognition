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
        face.embedding = FaceMapper.deserialize_embedding(row_proxy["embedding"]) if row_proxy["embedding"] else None
        return face

    @staticmethod
    def map_to_face_entities(result_proxy):
        faces = []
        for row_proxy in result_proxy:
            faces.append(FaceMapper.map_to_face_entity(row_proxy))
        return faces

    @staticmethod
    def deserialize_embedding(str_embedding):
        """
        :type str_embedding: np.array
        """
        return np.array(json.load(str_embedding))

    @staticmethod
    def serialize_embedding(embedding):
        return json.dumps(embedding.tolist())


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
            str_embedding = FaceMapper.serialize_embedding(embedding) if embedding is not None else 'NULL'
            connection.execute(f"UPDATE face SET embedding = '{str_embedding}' WHERE id={face_id}")

    def get_faces_without_embeddings(self, limit: int) -> [Face]:
        with self.get_connection() as connection:
            result_proxy = connection.execute(f'SELECT * FROM face i WHERE embedding IS NULL LIMIT {limit}')
            return FaceMapper.map_to_face_entities(result_proxy)

    def get_training_data(self):
        """Returns dict {embeddings:[], vk_users_ids:[]}"""
        embeddings = []
        user_ids = []
        with self.get_connection() as connection:
            result_proxy = connection.execute("SELECT embedding, vk_user_id FROM face "
                                              "JOIN image i on face.image_id = i.image_id "
                                              "JOIN vk_user_image vui on i.image_id = vui.image_id "
                                              "WHERE embedding IS NOT NULL")
            for row_proxy in result_proxy:
                embeddings.append(FaceMapper.deserialize_embedding(row_proxy['embedding']))
                user_ids.append(row_proxy['vk_user_id'])
            return {'embeddings': embeddings, 'users_ids': user_ids}
