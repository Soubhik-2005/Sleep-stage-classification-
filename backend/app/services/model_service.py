import json, threading
import numpy as np
from .. import config
from ml.src import config as C
from ml.src.preprocessing import normalize


class ModelService:
    def __init__(self):
        self.model, self.cfg, self.lock = None, None, threading.Lock()

    @property
    def available(self):
        return (C.MODEL_DIR / "sleep_stage_model.keras").exists() and \
               (C.MODEL_DIR / "preprocessing_config.json").exists()

    def load(self):
        with self.lock:
            if self.model is None:
                if not self.available:
                    raise RuntimeError("No trained model found in ml/saved_models. "
                                       "Run: python -m ml.src.train --download 10")
                import tensorflow as tf
                self.cfg = json.loads((C.MODEL_DIR / "preprocessing_config.json").read_text())
                self.model = tf.keras.models.load_model(C.MODEL_DIR / "sleep_stage_model.keras")
        return self.cfg

    def predict(self, X_uv):
        self.load()
        Xn = normalize(X_uv, self.cfg["mean"], self.cfg["std"])
        return self.model.predict(Xn, batch_size=64, verbose=0)


model_service = ModelService()
