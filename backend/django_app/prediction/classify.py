from django.core.files.uploadedfile import TemporaryUploadedFile, InMemoryUploadedFile
from PIL import Image
from prediction.verify import InputType
from tensorflow import keras
import tensorflow as tf
import numpy as np
import cv2
from collections import deque
from rest_framework.response import Response # TODO remove
import time
from prediction.state_enum import State
from prediction.apps import PredictionConfig


class Classifier():
    CLASS_NAMES = ["hentai", "porn", "neutral", "sexy", "drawings"]
    model = PredictionConfig.model
    img_width = 180
    img_height = 180
    labels_by_frame = {}

    state = {
        "progress": 0,
        "state": State.READY.value
    }

    def __init__(self):
        self.CLASS_NAMES.sort() # Alphabetical is important for mapping score to class name/label

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

        (score, label, frame) = self.get_score_and_label(predictions)

        msg = "This image likely belongs to {} with a {:.2f} percent confidence.".format(label, score)
        print(msg)

        return Response({
            "message": msg,
            "Predicted Classification": label,
            "Confidence": format(score, '.2f'),
            "content_type": file.content_type
        }, status=200)

    def classify_video(self, path):
        """
        Runs an .mp4 file against the machine learning model frame by frame.
        :param file: the file to run against the model, of type UploadedFile
        :return: an HTTPResponse with a list of tuples of format (confidence, classification)
        """
        print(type(path))
        print("Classifying video %s..." % path)
        video_stream = cv2.VideoCapture(path)
        print("Created video stream")
        (W, H) = (None, None)
        predictions = []
        q = deque(maxlen=10)
        i = 0
        total_frames = 100000
        start = time.time()
        self.state['state'] = State.IN_PROGRESS

        while True:
            (grabbed, frame) = video_stream.read()

            if not grabbed:
                break  # End of video

            if W is None or H is None:
                (H, W) = frame.shape[:2]

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.resize(frame, (self.img_width, self.img_height)).astype("float32")

            preds = self.model.predict(np.expand_dims(frame, axis=0))

            (score, label, frame_number) = self.get_score_and_label(preds)

            predictions.append((label, score, frame_number))

            self.get_contextual_label(q, label)

            i += 1
            self.state['progress'] = int(i/total_frames * 100)

        print("Cleaning up...")
        video_stream.release()
        end = time.time()

        msg = "Video classification finished in {} seconds.".format(end - start)
        print(msg)

        self.state['progress'] = int(i/total_frames * 100)
        self.state['state'] = State.COMPLETE.value
        self.state['message'] = msg
        self.state['duration'] = format(end - start, '.2f')
        self.state['prediction'] = predictions

    def get_number_of_frames(self, video):
        total = 0

        while True:
            (grabbed, frame) = video.read()
            
            if not grabbed:
                break
            
            total += 1
        
        return total

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
