"""Dataset builders. Synthetic by default; real datasets plug in via data/manifest.csv (see docs/DATASETS.md)."""
from __future__ import annotations

import numpy as np

from . import features as F
from . import synth as S
from .config import load

CFG = load()
N_CLASSES = len(CFG["classes"])


def range_features(clean_or_noisy: np.ndarray) -> np.ndarray:
    """4-d vector for the range MLP: [log rms, log centroid(Hz), log mean mel, periodicity]."""
    lm = F.log_mel(clean_or_noisy)
    pw = F.stft_power(clean_or_noisy)
    cen = np.mean([F.spectral_centroid(p) for p in pw])
    return np.array([np.log(F.rms(clean_or_noisy) + 1e-9), np.log(cen + 1.0), lm.mean(),
                     F.periodicity_score(F.onset_envelope(lm))])


def build_classifier_set(n, seed):
    rng = np.random.default_rng(seed)
    X, y = [], []
    for i in range(n):
        noisy, _, meta = S.make_example(i % N_CLASSES, rng)
        X.append(F.mfcc(noisy)); y.append(meta["label"])
    return np.stack(X).astype("float32"), np.array(y)


def build_denoiser_set(n, seed):
    rng = np.random.default_rng(seed)
    noisy_l, clean_l = [], []
    for _ in range(n):
        lab = int(rng.integers(0, 3))  # never "background": denoiser needs a signal to keep
        noisy, clean, _ = S.make_example(lab, rng)
        noisy_l.append(np.sqrt(F.mel_power(noisy))); clean_l.append(np.sqrt(F.mel_power(clean)))
    return np.stack(noisy_l).astype("float32"), np.stack(clean_l).astype("float32")


def build_range_set(n, seed):
    rng = np.random.default_rng(seed)
    X, y = [], []
    for _ in range(n):
        noisy, _, meta = S.make_example(S.LABELS["tap_knock"], rng)
        X.append(range_features(noisy)); y.append(meta["depth_m"])
    return np.stack(X).astype("float32"), np.array(y, dtype="float32")[:, None]
