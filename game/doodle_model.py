import numpy as np
from sklearn.preprocessing import LabelEncoder
import tensorflow as tf
from django.conf import settings
import os

keras = tf.keras
categories_path = os.path.join(settings.BASE_DIR, 'categories.npy')
# model_path = os.path.join(settings.BASE_DIR, 'doodles_model.h5')
model_path = os.path.join(settings.BASE_DIR, 'doodles_model_ver2.h5')


class DoodleModel:
    def __init__(self) -> None:
        self.model: keras.Model = keras.models.load_model(model_path)
        self.le: LabelEncoder = LabelEncoder()
        self.le.classes_ = np.load(categories_path)

    def set_data(self, data: list) -> None:
        self.grid: list[list] = [[0 for _ in range(28)] for _ in range(28)]
        for i in range(28):
            for j in range(28):
                self.grid[i][j] = data[i * 28 + j]
        self.grid: np.ndarray = np.array(self.grid, dtype=float)

    def top3_predict(self, grid: np.ndarray) -> list[list]:
        '''
            Return the top 3 most prediction from the model, represents by 
            the prediction and corresponding probability numpy array. 
        '''
        grid = grid.reshape(-1, 28, 28, 1)
        # print(self.grid.shape, self.grid)
        prediction = self.model.predict(grid)
        indices = np.argpartition(prediction[0], -3)[-3:]
        prediction_and_prob = []
        prediction_and_prob.append(self.le.inverse_transform(indices).tolist())
        prediction_and_prob.append(prediction[0][indices].tolist())

        return prediction_and_prob
