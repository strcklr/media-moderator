# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from prediction.apps import PredictionConfig
from PIL import Image
from prediction.verify import InputType
from tensorflow import keras
import tensorflow as tf
import numpy as np
import prediction.verify as verify
import time
import cv2
from collections import deque


class InvalidFormatError(Exception):
    pass


def save_to_disk(file):
    """
    Saves a given file to disk
    :param file: UploadedFile to save to disk
    :return: the path to the file
    """
    import os
    if not os.path.isdir(settings.MEDIA_ROOT + 'tmp/'):
        os.mkdir(settings.MEDIA_ROOT + 'tmp/')

    with default_storage.open('tmp/' + file.name, 'wb+') as destination:
        print("Destination: %s" % repr(destination))
        for chunk in file.chunks():
            destination.write(chunk)

    return os.path.join(settings.MEDIA_ROOT, 'tmp/' + file.name)


class MediaPredict(APIView):
    """
    Class responsible for handling a POST with a file attachment
    and running it through the model to return an HTTP response
    with the prediction and confidence metrics.
    """
    CLASS_NAMES = ["hentai", "porn", "neutral", "sexy", "drawings"]
    # drawings, hentai, neutral, porn, sexy
    model = PredictionConfig.model
    img_width = 180
    img_height = 180
    labels_by_frame = {}

    def __init__(self):
        self.CLASS_NAMES.sort()  # Alphabetical

    def _process(self, data):
        """
        Processes the HTTP request data
        :param data: the HTTPRequest.data to be processed
        :return: an HTTPResponse
        """

        file = data['file']

        try:
            itype = verify.get_input_type(file)
        except IOError as e:
            print(e)
            return Response({
                "error": "Failed to verify file, likely due to the file being corrupt."
            }, status=400)

        try:
            if itype == verify.InputType.JPEG:
                return self.classify_image(file)
            elif itype == verify.InputType.MP4:
                return self.classify_video(file)
            else:
                return Response({
                    "error": "File type is not supported!",
                    "file": file.name
                }, status=400)
        except Exception as e:
            print(e)
            return Response({
                "message": "An unexpected error has ocurred!",
                "error": repr(e),
            }, status=500)

    def classify_image(self, file):
        if isinstance(file, TemporaryUploadedFile):
            path = file.temporary_file_path()
            img = keras.preprocessing.image.load_img(
                path, target_size=(180, 180)
            )

        elif isinstance(file, InMemoryUploadedFile):
            img = Image.open(file)
            img = img.resize((180, 180))

        img_array = keras.preprocessing.image.img_to_array(img)
        img_array = tf.expand_dims(img_array, 0)  # Create a batch
        print(img_array.shape.as_list())

        predictions = self.model.predict(img_array)

        (score, label) = self.get_score_and_label(predictions)

        msg = "This image likely belongs to {} with a {:.2f} percent confidence.".format(label, score)
        print(msg)

        return Response({
            "message": msg,
            "Predicted Classification": label,
            "Confidence": format(score, '.2f'),
            "content_type": file.content_type
        }, status=200)

    def classify_video(self, file):
        """
        Runs an .mp4 file against the machine learning model frame by frame.
        :param file: the file to run against the model, of type UploadedFile
        :return: an HTTPResponse with a list of tuples of format (confidence, classification)
        """
        path = save_to_disk(file)
        print(type(path))
        print("Classifying video %s..." % path)
        video_stream = cv2.VideoCapture(path)
        print("Created video stream")
        (W, H) = (None, None)
        predictions = []
        q = deque(maxlen=10)
        i = 0
        start = time.time()

        while True:
            # grabbed, frame = (None, None)

            # for i in range(0, 4):  # Skip 4 frames to speed up processing time
            (grabbed, frame) = video_stream.read()

            if not grabbed:
                break  # End of video

            if W is None or H is None:
                (H, W) = frame.shape[:2]

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.img_width, self.img_height)).astype("float32")

            preds = self.model.predict(np.expand_dims(frame, axis=0))

            (score, label, index) = self.get_score_and_label(preds)

            predictions.append((label, score, index))

            self.get_contextual_label(q, label)

            i += 1

        print("Cleaning up...")
        video_stream.release()
        end = time.time()

        msg = "Video classification finished in {} seconds.".format(end - start)
        print(msg)

        return Response({
            "message": msg,
            "predictions": predictions,
        }, status=200)

    def get_contextual_label(self, queue, label):
        """
        Retrieves the label for a frame while taking in the context of surrounding frames to remove prediction flickering.
        This will need to be readdressed, as it is very possible a video could display some NSFW content for less than 10 frames,
        defeating the purpose of this project entirely.
        """
        import operator
        assert isinstance(queue, deque)
        popped = None

        if queue.count == queue.maxlen:
            popped = queue.popleft()

        queue.append(label)

        if popped in self.labels_by_frame and self.labels_by_frame[popped] > 0:
            self.labels_by_frame[popped] -= 1
        if label in self.labels_by_frame:
            self.labels_by_frame[label] += 1
        else:
            self.labels_by_frame[label] = 1

        return max(self.labels_by_frame.items(), key=operator.itemgetter(1))[0]

    def get_score_and_label(self, prediction):
        score = tf.nn.softmax(prediction[0])
        return 100 * np.max(score), self.CLASS_NAMES[np.argmax(score)], np.argmax(score)

    def post(self, request, format=None):
        print(request.data)
        return self._process(request.data)


