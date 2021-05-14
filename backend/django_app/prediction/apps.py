# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from tensorflow import keras
import os


class PredictionConfig(AppConfig):
    name = 'prediction'
    img_height = 180
    img_width = 180
    model_path = "prediction/model" # TODO fix this path
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODEL_FOLDER = os.path.join(BASE_DIR, model_path)

    print("-------- FILES ---------")
    print(os.listdir(BASE_DIR))

    model = keras.models.load_model(MODEL_FOLDER)
