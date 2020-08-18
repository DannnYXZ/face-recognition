import cv2

from face_detector import FaceDetector
from face_embedder import FaceEmbedder
from repository.image_repository import ImageRepository


class FindFaceService:
    def __init__(self,
                 image_repository: ImageRepository,
                 face_embedder: FaceEmbedder,
                 face_detector: FaceDetector):
        self.face_embedder = face_embedder
        self.face_detector = face_detector
        self.image_repository = image_repository

    def extract_faces_in_db(self, confidence):
        while True:
            images = self.image_repository.get_images_without_faces(1000)
            if not images:
                return
            for image_entity in images:
                image = cv2.imread(image_entity.path)
                detections = self.face_detector.detect_faces(image, confidence)
                self.image_repository.save_face_regions(image_entity.id, detections)

    def extract_embeddings_in_db(self):
        """Extracts and saves embeddings for each face in db"""
        while True:
            faces_without_embeddings = self.image_repository.get_faces_without_embeddings(1000)
            if not faces_without_embeddings:
                return
            images_with_faces = self.image_repository.get_images_with_faces(faces_without_embeddings)
            for image_entity in images_with_faces:
                image = cv2.imread(image_entity.path)
                for face in image_entity.faces:
                    embedding = self.face_embedder.extract_embedding(image,
                                                                     face_region=[face.start_x, face.start_y, face.end_x, face.end_y])
                    self.image_repository.save_face_embedding(face.id, embedding)

    def train_recognition_model(self):
        pass
