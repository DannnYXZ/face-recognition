import cv2


class FaceEmbedder:
    def __init__(self, torch_model_path):
        self.embedder = cv2.dnn.readNetFromTorch(torch_model_path)

    def extract_embedding(self, image, face_region: (int, int, int, int)):
        """
        :param image: image as array of colors
        :param face_region: (x0, y0, x1, y1)
        :return: 128-d embedding vector
        """
        (startX, startY, endX, endY) = face_region
        face_image = image[startY:endY, startX:endX]
        (fH, fW) = face_image.shape[:2]

        # construct a blob for the face ROI, then pass the blob
        # through our face embedding model to obtain the 128-d
        faceBlob = cv2.dnn.blobFromImage(face_image, 1.0 / 255,
                                         (96, 96), (0, 0, 0), swapRB=True, crop=False)
        self.embedder.setInput(faceBlob)
        vec = self.embedder.forward().flatten()
        return vec
        # knownNames.append(name)
        # knownEmbeddings.append(vec.flatten())
