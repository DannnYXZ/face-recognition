import pickle

from sklearn.svm import SVC

from repository.face_repository import FaceRepository


class FaceRecognizer:
    def __init__(self):
        self.recognizer = SVC(C=1.0, kernel='linear', probability=True)

    def load_model(self, model_pickle_path):
        self.recognizer = pickle.loads(open(model_pickle_path, "rb").read())

    def save_model(self, output_pickle_path):
        f = open(output_pickle_path, "wb")
        f.write(pickle.dumps(self.recognizer))

    def train_model_from_db(self, face_repository: FaceRepository):
        training_data = face_repository.get_training_data()
        self.recognizer.fit(training_data['embeddings'], training_data['users_ids'])

    def recognize(self, image_path):