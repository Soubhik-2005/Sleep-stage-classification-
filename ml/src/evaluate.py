import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, cohen_kappa_score
from . import config as C


def evaluate_model(model, X, y):
    pred = model.predict(X, batch_size=128, verbose=0).argmax(1)
    rep = classification_report(y, pred, labels=range(5), target_names=C.CLASS_NAMES,
                                output_dict=True, zero_division=0)
    cm = confusion_matrix(y, pred, labels=range(5))
    print(classification_report(y, pred, labels=range(5), target_names=C.CLASS_NAMES, zero_division=0))
    print("Confusion matrix (rows = true):\n", cm)
    return {"accuracy": float((pred == y).mean()), "macro_f1": float(rep["macro avg"]["f1-score"]),
            "kappa": float(cohen_kappa_score(y, pred)), "per_class": {k: rep[k] for k in C.CLASS_NAMES},
            "confusion_matrix": cm.tolist()}
