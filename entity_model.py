import numpy as np


class Face:
    def __init__(self):
        self.id: int
        self.image_id: int
        self.start_x: int
        self.start_y: int
        self.end_x: int
        self.end_y: int
        self.confidence: float
        self.embedding: []  # np.array


class Image:
    def __init__(self):
        self.id: int
        self.path: str
        self.url: str
        self.type: str
        self.faces: [Face]
