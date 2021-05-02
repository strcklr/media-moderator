# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.views import APIView
from prediction.apps import PredictionConfig
from tensorflow import keras
from tensorflow.keras.layers import Conv2D, MaxPooling2D
from PIL import Image
from django.core.files.uploadedfile import UploadedFile, TemporaryUploadedFile, InMemoryUploadedFile
import django
import io
import tensorflow as tf
import numpy as np


# TODO this
def _is_image(file):
    return True


class InvalidFormatError(Exception):
    pass


class MediaPredict(APIView):
    CLASS_NAMES = ["hentai", "porn", "neutral"]
    model = PredictionConfig.model

    def _process(self, data):
        file = data['file']
        if _is_image(file):

            img = None

            if isinstance(file, TemporaryUploadedFile):
                path = file.temporary_file_path()
                img = keras.preprocessing.image.load_img(
                    path, target_size=(180, 180)
                )

            elif isinstance(file, InMemoryUploadedFile):
                img = Image.open(file)
                img = img.resize((180, 180))

            else:
                # TODO need to rebuild model with layer for shape (None, 180, 180, 4)
                raise InvalidFormatError("Uploaded format is not yet supported!")

            img_array = keras.preprocessing.image.img_to_array(img)
            img_array = tf.expand_dims(img_array, 0)  # Create a batch
            print(img_array.shape.as_list())

            predictions = self.model.predict(img_array)

            (score, label) = self.get_score_and_label(predictions)

            print(
                "This image likely belongs to {} with a {:.2f} percent confidence.".format(label, score)
            )

            return {
                    "Predicted Classification": label,
                    "Confidence": score
                    }

    def post(self, request, format=None):
        data = request.data
        keys = []
        values = []
        json_val = {}
        for key in data:
            keys.append(key)
            values.append(data[key])
            json_val[key] = data[key]

        print(request.data)

        try:
            res = self._process(request.data)
            return Response(res, status=200)
        except Exception as e:
            print(e)
            return Response({"Error": "Exception was thrown!"}, status=500)

    def get_score_and_label(self, prediction):
        score = tf.nn.softmax(prediction[0])
        return 100 * np.max(score), self.CLASS_NAMES[np.argmax(score)]
