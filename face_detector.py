import cv2
import imutils
import numpy as np


class FaceDetector:
    def __init__(self, proto_path, model_path):
        self.detector = cv2.dnn.readNetFromCaffe(proto_path, model_path)

    # load the image, resize it to have a width of 600 pixels (while
    # maintaining the aspect ratio), and then grab the image
    # dimensions
    def detect_faces(self, image, confidence) -> [(int, int, int, int, float)]:
        """
        :param confidence: ignore face detection threshold
        :argument image: image as array of colors
        :return: array of tuples (startX, startY, endX, endY, confidence)
        """
        faces = []
        if image is None:
            return faces
        image = imutils.resize(image, width=600)
        (h, w) = image.shape[:2]

        image_blob = cv2.dnn.blobFromImage(
            cv2.resize(image, (300, 300)), 1.0, (300, 300),
            (104.0, 177.0, 123.0), swapRB=False, crop=False)

        self.detector.setInput(image_blob)
        detections = self.detector.forward()
        for i in range(0, detections.shape[2]):
            actual_confidence = detections[0, 0, i, 2]
            if actual_confidence > confidence:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                faces.append((*box.astype("int"), actual_confidence))
        return faces

    def show_faces(self, image_path, faces_with_confidence):
        image = cv2.imread(image_path)
        if image is None:
            return
        image = imutils.resize(image, width=600)
        for (startX, startY, endX, endY, confidence) in faces_with_confidence:
            text = "{:.2f}%".format(confidence * 100)
            TEXT_HEIGHT = 10
            text_y = startY - TEXT_HEIGHT if startY - TEXT_HEIGHT > TEXT_HEIGHT else startY + 1
            cv2.rectangle(image, (startX, startY), (endX, endY),
                          (0, 0, 255), 2)
            cv2.putText(image, text, (startX, text_y),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        cv2.imshow("Output", image)
        cv2.waitKey(0)
