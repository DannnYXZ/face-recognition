class Face:
    image_id: int
    start_x: int
    start_y: int
    end_x: int
    end_y: int
    embedding: str


class Image:
    image_id: int
    path: str
    url: str
    faces: [Face]


class ImageRepository:
    def __init__(self, data_source):
        self.data_source = data_source

    def get_images_with_faces_without_embeddings(self, limit: int) -> [Face]:
        pass

    def get_images_without_faces(self, limit: int) -> [Image]:
        pass

    def save_face_regions(self, image_id, detections):
        pass

    def save_embedding(self, image_id, embedding):
        pass
