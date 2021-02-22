import sys
import time
import numpy as np
import tensorflow as tf
import cv2
import dataholder as data
from collections import deque
from tensorflow import keras

img_height = 180
img_width = 180
model = keras.models.load_model("model")
contextual_labels = {}


def main(argv):
    path = argv[1]
    if path.endswith(".mp4"):
        classify_video(path)
        return
    print("Classifying image %s" % path)
    img = keras.preprocessing.image.load_img(
        path, target_size=(img_height, img_width)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    start = time.time()
    predictions = model.predict(img_array)
    end = time.time()
    (score, label) = get_score_and_label(predictions)

    print(
        "This image likely belongs to {} with a {:.2f} percent confidence ({} seconds)."
            .format(label, score, end - start)
    )


def get_score_and_label(prediction):
    score = tf.nn.softmax(prediction[0])
    return 100 * np.max(score), data.CLASS_NAMES[np.argmax(score)]


def get_contextual_label(queue, label):
    import operator
    assert isinstance(queue, deque)
    popped = None
    if queue.count == queue.maxlen:
        popped = queue.popleft()
    queue.append(label)
    if popped in contextual_labels and contextual_labels[popped] > 0:
        contextual_labels[popped] -= 1
    if label in contextual_labels:
        contextual_labels[label] += 1
    else:
        contextual_labels[label] = 1
    return max(contextual_labels.items(), key=operator.itemgetter(1))[0]


def classify_video(path):
    print("Classifying video %s..." % path)
    video_stream = cv2.VideoCapture(path)
    writer = None
    (W, H) = (None, None)
    predictions = {}
    q = deque(maxlen=10)
    i = 0
    start = time.time()

    while True:
        grabbed, frame = (None, None)

        # for i in range(0, 4):  # Skip 4 frames to speed up processing time
        (grabbed, frame) = video_stream.read()

        if not grabbed:
            break  # End of video

        if W is None or H is None:
            (H, W) = frame.shape[:2]

        i += 1

        # output = frame.copy()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = cv2.resize(frame, (img_width, img_height)).astype("float32")
        #
        preds = model.predict(np.expand_dims(frame, axis=0))
        #
        (score, label) = get_score_and_label(preds)

        predictions[label] = score

        get_contextual_label(q, label)
        # Write out the frame with the classification embedded
        # cv2.putText(output, label, (35, 50), cv2.FONT_HERSHEY_SIMPLEX,
        #             1.25, (0, 255, 0), 5)

        # if writer is None:
        #     fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        #     writer = cv2.VideoWriter("predicted-video.mp4", fourcc, 30,
        #                              (W, H), True)
        #
        # print ("Writing frame %d" % i)
        # writer.write(output)

    print("Cleaning up...")
    # writer.release()
    video_stream.release()
    end = time.time()
    print("Video classification finished in {} seconds.".format(end - start))


def classify_image(path):
    print("Classifying image %s" % path)


if __name__ == "__main__":
    main(sys.argv)
