import tensorflow as tf
from tensorflow.keras import layers, models
from . import config as C


def build_model(n_channels=len(C.CHANNELS), n_classes=len(C.CLASS_NAMES), samples=C.SAMPLES):
    """1D CNN baseline: (3000, 3) -> 5 softmax probabilities."""
    def block(x, filters, kernel, pool=True):
        x = layers.Conv1D(filters, kernel, padding="same")(x)
        x = layers.BatchNormalization()(x)
        x = layers.Activation("relu")(x)
        return layers.MaxPooling1D(4)(x) if pool else x

    inp = layers.Input((samples, n_channels))
    x = block(inp, 32, 7)
    x = block(x, 64, 7)
    x = block(x, 128, 5, pool=False)
    x = layers.GlobalAveragePooling1D()(x)
    x = layers.Dense(64, activation="relu")(x)
    x = layers.Dropout(0.5)(x)
    out = layers.Dense(n_classes, activation="softmax")(x)
    model = models.Model(inp, out, name="sleep_cnn")
    model.compile(optimizer=tf.keras.optimizers.Adam(1e-3),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])
    return model
