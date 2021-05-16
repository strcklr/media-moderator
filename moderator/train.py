import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt
import os

from dataholder import DataHolder
from tensorflow.keras import layers
from tensorflow.keras.models import Sequential
from keras.layers import Bidirectional, CuDNNLSTM


def train():
    if not os.path.isdir("../checkpoints"):
        os.mkdir("../checkpoints")

    data = DataHolder('S://data/train')

    batch_size = 8
    img_height = 180
    img_width = 180

    data.train_set = tf.keras.preprocessing.image_dataset_from_directory(
        data.data_dir,
        validation_split=0.2,
        subset="training",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    """
    The current dataset is split into a train and test already, so the validation split is unnecessary
    """
    data.val_set = tf.keras.preprocessing.image_dataset_from_directory(
        data.data_dir,
        validation_split=0.2,
        subset="validation",
        seed=123,
        image_size=(img_height, img_width),
        batch_size=batch_size)

    # Performance configuration
    AUTOTUNE = tf.data.experimental.AUTOTUNE
    data.train_set = data.train_set.cache().prefetch(buffer_size=AUTOTUNE)
    data.val_set = data.val_set.cache().prefetch(buffer_size=AUTOTUNE)

    # Standardize the data
    normalization_layer = layers.experimental.preprocessing.Rescaling(1. / 255)
    normalized_set = data.train_set.map(lambda x, y: (normalization_layer(x), y))
    normalized_set.shuffle(1000)
    image_batch, labels_batch = next(iter(normalized_set))
    print(np.min(image_batch[0]), np.max(image_batch[0]))

    # Data augmentation
    data_augmentation = tf.keras.Sequential(
        [
            layers.experimental.preprocessing.RandomFlip("horizontal",
                                                         input_shape=(img_height,
                                                                      img_width,
                                                                      3)),
            layers.experimental.preprocessing.RandomRotation(0.1),
            layers.experimental.preprocessing.RandomZoom(0.1),
        ]
    )

    # Create the model
    classes = 5
    model = Sequential([
        data_augmentation,
        layers.experimental.preprocessing.Rescaling(1. / 255, input_shape=(img_height, img_width, 3)),
        layers.Conv2D(16, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(32, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Conv2D(64, 3, padding='same', activation='relu'),
        layers.MaxPooling2D(),
        layers.Dropout(0.2),
        layers.Flatten(),
        layers.Dense(128, activation='relu'),
        layers.Dense(classes),
    ])

    model.compile(optimizer='adam',
                  loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
                  metrics=['accuracy'])

    model.summary()

    checkpoint_path = "checkpoints/cp-{epoch:04d}.ckpt"
    checkpoint_dir = os.path.dirname(checkpoint_path)

    # Create a callback that saves the model's weights
    cp_callback = tf.keras.callbacks.ModelCheckpoint(filepath=checkpoint_path,
                                                     save_weights_only=True,
                                                     verbose=1)

    # Save the weights using the `checkpoint_path` format
    model.save_weights(checkpoint_path.format(epoch=0))

    # Train the model
    epochs = 10
    history = model.fit(
        data.train_set,
        validation_data=data.val_set,
        epochs=epochs,
        callbacks=[cp_callback]
    )

    accuracy = history.history['accuracy']
    val_acc = history.history['val_accuracy']

    loss = history.history['loss']
    val_loss = history.history['val_loss']

    epochs_range = range(epochs)

    show_plot(accuracy, val_acc, val_loss, loss, epochs_range)

    # Save the entire model as a SavedModel.
    model.save('model')


def show_plot(accuracy, val_acc, val_loss, loss, epochs_range):
    plt.figure(figsize=(8, 8))
    plt.subplot(1, 2, 1)
    plt.plot(epochs_range, accuracy, label="Training Accuracy")
    plt.plot(epochs_range, val_acc, label="Validation Accuracy")
    plt.legend(loc="lower right")
    plt.title('Training and Validation Accuracy')

    plt.subplot(1, 2, 2)
    plt.plot(epochs_range, loss, label="Training Loss")
    plt.plot(epochs_range, val_loss, label="Validation Loss")
    plt.title("Training and Validation Loss")
    # plt.show()
    plt.savefig("accuracy_graph.png")


train()
