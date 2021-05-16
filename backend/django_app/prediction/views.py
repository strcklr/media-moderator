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
from pytube import YouTube
from collections import deque
from prediction.state_enum import State
from prediction.classify import Classifier

class InvalidFormatError(Exception):
    pass


class MediaPredict(APIView):
    """
    Class responsible for handling API calls and synchronizing that with the prediction model.
    """
    model = PredictionConfig.model
    classifier = Classifier()

    yt = None

    yt_download_state = {
        "progress": 0,
        "state": State.READY.value  
    }

    def __init__(self):
        self.CLASS_NAMES.sort()  # Alphabetical
    
    def post(self, request, format=None):
        print(request.data)
        self._process(request.data)
        return Response({
            "message": "Processing request"
        }, status=200)

    def get(self, request):
        state = {
            "error": "Unknown progress request!"
        }

        value = request.GET.get("progress")
        if "youtube" == value and self.yt is not None:
            self.yt_download_state['progress'] = self.yt.percent
            self.yt_download_state['state'] = State.IN_PROGRESS.value
            state = self.yt_download_state
        elif "prediction" == value:
            state = self.prediction_state
    
        return Response(state, status=200)

