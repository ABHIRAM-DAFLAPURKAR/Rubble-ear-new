"""CLI: python -m rubble_ear.train {denoiser|classifier|range} [--n N] [--epochs E] [--smoke]
Writes Keras model to models/<name>.keras and metrics JSON to models/<name>.metrics.json."""
from __future__ import annotations

import argparse
import json

import numpy as np

from . import data, models
from .config import ROOT, load

CFG = load()
OUT = ROOT / "models"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("phase", choices=["denoiser", "classifier", "range"])
    ap.add_argument("--n", type=int, default=CFG["train"]["n_examples"])
    ap.add_argument("--epochs", type=int, default=CFG["train"]["epochs"])
    ap.add_argument("--smoke", action="store_true", help="tiny run to prove the loop works")
    a = ap.parse_args()
    if a.smoke:
        a.n, a.epochs = 24, 1
    import tensorflow as tf
    tf.keras.utils.set_random_seed(CFG["train"]["seed"])
    OUT.mkdir(exist_ok=True)
    seed, bs = CFG["train"]["seed"], CFG["train"]["batch_size"]
    opt = tf.keras.optimizers.Adam(CFG["train"]["lr"])

    if a.phase == "denoiser":
        noisy, clean = data.build_denoiser_set(a.n, seed)
        m = models.build_crnn_denoiser(CFG["audio"]["n_mels"])
        # target ideal ratio mask, clipped to [0,1]
        target = np.clip(clean / (noisy + 1e-6), 0, 1)
        m.compile(opt, "mse")
        h = m.fit(noisy[..., None], target, epochs=a.epochs, batch_size=bs, validation_split=0.2, verbose=2)
        metrics = {"val_mse": float(h.history["val_loss"][-1])}
    elif a.phase == "classifier":
        X, y = data.build_classifier_set(a.n, seed)
        m = models.build_fusion_classifier(use_yamnet=False)
        m.compile(opt, "sparse_categorical_crossentropy", metrics=["accuracy"])
        h = m.fit(X, y, epochs=a.epochs, batch_size=bs, validation_split=0.2, verbose=2)
        metrics = {"val_accuracy": float(h.history["val_accuracy"][-1])}
    else:
        X, y = data.build_range_set(a.n, seed)
        mu, sd = X.mean(0), X.std(0) + 1e-6
        m = models.build_mlp_regressor()
        m.compile(opt, "mse", metrics=["mae"])
        h = m.fit((X - mu) / sd, y, epochs=a.epochs, batch_size=bs, validation_split=0.2, verbose=2)
        metrics = {"val_mae_m": float(h.history["val_mae"][-1]), "mu": mu.tolist(), "sd": sd.tolist()}
    m.save(OUT / f"{a.phase}.keras")
    (OUT / f"{a.phase}.metrics.json").write_text(json.dumps({**metrics, "smoke": a.smoke}, indent=2))
    print("saved", OUT / f"{a.phase}.keras", metrics)


if __name__ == "__main__":
    main()
