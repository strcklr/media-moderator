import sys
import time
import numpy as np
import tensorflow as tf
import PIL
from tensorflow import keras


def main(argv):
    img_height = 180
    img_width = 180
    path = argv[1]
    print("Classifying image %s" % path)
    img = keras.preprocessing.image.load_img(
        path, target_size=(img_height, img_width)
    )
    img_array = keras.preprocessing.image.img_to_array(img)
    img_array = tf.expand_dims(img_array, 0)  # Create a batch

    model = keras.models.load_model("model")
    model.summary()

    start = time.time()
    predictions = model.predict(img_array)
    end = time.time()
    score = tf.nn.softmax(predictions[0])

    class_names = ["hentai", "porn", "neutral"]  # Alphabetical
    class_names = sorted(class_names)

    print(
        "This image likely belongs to {} with a {:.2f} percent confidence ({} seconds)."
        .format(class_names[np.argmax(score)], 100 * np.max(score), end - start)
    )


if __name__ == "__main__":
    main(sys.argv)
