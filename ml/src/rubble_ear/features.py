"""Reference feature extraction (Eq.1-6). The TypeScript port in web/lib/dsp MUST match this
numerically (see parity/golden.json). float64 everywhere. No librosa: keep it reproducible."""
from __future__ import annotations

import numpy as np
from scipy.fft import dct

from .config import load

A = load()["audio"]


def hann(n: int) -> np.ndarray:
    """Periodic Hann window."""
    return 0.5 - 0.5 * np.cos(2 * np.pi * np.arange(n) / n)


def frame_count(n_samples: int, win: int = A["win"], hop: int = A["hop"]) -> int:
    return 0 if n_samples < win else 1 + (n_samples - win) // hop


def stft_power(x: np.ndarray, win=A["win"], hop=A["hop"], n_fft=A["n_fft"]) -> np.ndarray:
    """Eq.1 -> power spectrogram, shape (frames, n_fft//2+1). No centre padding."""
    x = np.asarray(x, dtype=np.float64)
    n = frame_count(len(x), win, hop)
    w = hann(win)
    out = np.empty((n, n_fft // 2 + 1))
    for i in range(n):
        seg = np.zeros(n_fft)
        seg[:win] = x[i * hop : i * hop + win] * w
        spec = np.fft.rfft(seg)
        out[i] = spec.real**2 + spec.imag**2
    return out


def hz_to_mel(f):
    """Eq.2 (HTK)."""
    return 2595.0 * np.log10(1.0 + np.asarray(f, dtype=np.float64) / 700.0)


def mel_to_hz(m):
    return 700.0 * (10.0 ** (np.asarray(m, dtype=np.float64) / 2595.0) - 1.0)


def mel_filterbank(sr=A["sr"], n_fft=A["n_fft"], n_mels=A["n_mels"], fmin=A["fmin"], fmax=A["fmax"]):
    """Triangular, un-normalised. Shape (n_mels, n_fft//2+1)."""
    pts = mel_to_hz(np.linspace(hz_to_mel(fmin), hz_to_mel(fmax), n_mels + 2))
    freqs = np.arange(n_fft // 2 + 1) * sr / n_fft
    fb = np.zeros((n_mels, len(freqs)))
    for m in range(n_mels):
        l, c, r = pts[m], pts[m + 1], pts[m + 2]
        fb[m] = np.maximum(0.0, np.minimum((freqs - l) / (c - l), (r - freqs) / (r - c)))
    return fb


_FB = mel_filterbank()


def mel_power(x: np.ndarray) -> np.ndarray:
    return stft_power(x) @ _FB.T


def log_mel(x: np.ndarray, eps: float = A["eps"]) -> np.ndarray:
    """Natural-log mel power, shape (frames, n_mels)."""
    return np.log(mel_power(x) + eps)


def mfcc(x: np.ndarray, n_mfcc: int = 13) -> np.ndarray:
    """Eq.3 via orthonormal DCT-II of log-mel."""
    return dct(log_mel(x), type=2, axis=1, norm="ortho")[:, :n_mfcc]


def rms(x: np.ndarray) -> float:
    """Eq.5."""
    x = np.asarray(x, dtype=np.float64)
    return float(np.sqrt(np.mean(x**2)))


def zcr(x: np.ndarray) -> float:
    """Eq.4."""
    s = np.sign(np.asarray(x, dtype=np.float64))
    return float(np.sum(np.abs(np.diff(s))) / 2.0 / (len(s) - 1))


def spectral_centroid(power_frame: np.ndarray, sr=A["sr"], n_fft=A["n_fft"]) -> float:
    """Eq.6 on one power-spectrum frame (uses magnitude)."""
    mag = np.sqrt(power_frame)
    f = np.arange(len(mag)) * sr / n_fft
    return float((f * mag).sum() / (mag.sum() + 1e-12))


def onset_envelope(lm: np.ndarray) -> np.ndarray:
    """Half-wave rectified spectral flux of a log-mel matrix. Length frames."""
    d = np.maximum(0.0, np.diff(lm, axis=0)).sum(axis=1)
    return np.concatenate([[0.0], d])


def periodicity_score(env: np.ndarray, hop=A["hop"], sr=A["sr"], lo_s=0.15, hi_s=1.5) -> float:
    """Max normalised autocorrelation of the onset envelope for lags in [lo_s, hi_s].
    High for rhythmic human tapping, low for random settling/machinery. Range ~[0,1]."""
    e = env - env.mean()
    denom = float((e * e).sum())
    if denom < 1e-12:
        return 0.0
    fps = sr / hop
    lo, hi = int(lo_s * fps), min(int(hi_s * fps), len(e) - 1)
    if hi <= lo:
        return 0.0
    ac = np.array([(e[:-k] * e[k:]).sum() for k in range(lo, hi + 1)]) / denom
    return float(max(0.0, ac.max()))
