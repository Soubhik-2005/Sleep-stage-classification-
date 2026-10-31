"""Train the sleep-stage CNN.

Real data:      python -m ml.src.train --download 10         (downloads Sleep-EDF via MNE)
                python -m ml.src.train --data-dir dataset/raw
Pipeline test:  python -m ml.src.train --synthetic --epochs 3   (meaningless accuracy!)
"""
import argparse, json
import numpy as np
from . import config as C
from .preprocessing import normalize
from .model import build_model
from .evaluate import evaluate_model


def split_by_subject(subjects, seed=42, fracs=(0.70, 0.15, 0.15)):
    """Subject-wise split -> no leakage between train/val/test."""
    uniq = np.array(sorted(set(subjects)))
    rng = np.random.default_rng(seed); rng.shuffle(uniq)
    n = len(uniq)
    if n < 3: raise ValueError("Need at least 3 subjects for a subject-wise split.")
    n_val = max(1, round(n * fracs[1])); n_test = max(1, round(n * fracs[2]))
    test, val, train = uniq[:n_test], uniq[n_test:n_test + n_val], uniq[n_test + n_val:]
    return [np.isin(subjects, g) for g in (train, val, test)]


def load_real(args):
    from .data_loader import find_pairs, load_cached, subject_id, download_sleep_edf
    pairs = download_sleep_edf(args.download) if args.download else find_pairs(args.data_dir)
    Xs, ys, subj = [], [], []
    for i, (psg, hyp) in enumerate(pairs, 1):
        print(f"[{i}/{len(pairs)}] {psg.name}")
        X, y = load_cached(psg, hyp)
        Xs.append(X); ys.append(y); subj += [subject_id(psg)] * len(y)
    return np.concatenate(Xs), np.concatenate(ys), np.array(subj)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data-dir", default=str(C.RAW_DIR))
    ap.add_argument("--download", type=int, default=0, help="download N Sleep-EDF subjects first")
    ap.add_argument("--synthetic", action="store_true")
    ap.add_argument("--epochs", type=int, default=30)
    ap.add_argument("--batch-size", type=int, default=64)
    a = ap.parse_args()

    if a.synthetic:
        from .synthetic import make_dataset
        X, y, subj = make_dataset(8, 300)
    else:
        X, y, subj = load_real(a)
    print("X", X.shape, "class counts", np.bincount(y, minlength=5))

    tr, va, te = split_by_subject(subj)
    mean = X[tr].mean(axis=(0, 1)); std = X[tr].std(axis=(0, 1))     # training statistics only
    Xtr, Xva, Xte = (normalize(X[m], mean, std) for m in (tr, va, te))
    ytr, yva, yte = y[tr], y[va], y[te]

    from sklearn.utils.class_weight import compute_class_weight
    import tensorflow as tf
    cls = np.unique(ytr)
    cw = dict(zip(cls.tolist(), compute_class_weight("balanced", classes=cls, y=ytr)))  # helps N1
    model = build_model()
    model.fit(Xtr, ytr, validation_data=(Xva, yva), epochs=a.epochs, batch_size=a.batch_size,
              class_weight=cw, verbose=2, callbacks=[tf.keras.callbacks.EarlyStopping(
                  patience=6, restore_best_weights=True, monitor="val_loss")])

    metrics = evaluate_model(model, Xte, yte)
    C.MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(C.MODEL_DIR / "sleep_stage_model.keras")
    cfg = {"model_version": C.MODEL_VERSION + ("_synthetic" if a.synthetic else ""),
           "channels": C.CHANNELS, "sfreq": C.SFREQ, "epoch_sec": C.EPOCH_SEC,
           "bandpass": C.BANDPASS, "class_names": C.CLASS_NAMES,
           "mean": mean.tolist(), "std": std.tolist(), "synthetic": a.synthetic,
           "test_metrics": metrics}
    (C.MODEL_DIR / "preprocessing_config.json").write_text(json.dumps(cfg, indent=2))
    print(f"Saved model + config to {C.MODEL_DIR}  (test acc {metrics['accuracy']:.3f}, "
          f"macro-F1 {metrics['macro_f1']:.3f})")


if __name__ == "__main__":
    main()
