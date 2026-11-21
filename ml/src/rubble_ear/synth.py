"""Physically-motivated synthetic clips so the whole pipeline runs with ZERO downloads (CI-safe).
Real datasets (docs/DATASETS.md) replace/augment these via the same interfaces."""
from __future__ import annotations

import numpy as np
from scipy.signal import butter, lfilter

from .config import load

CFG = load()
SR = CFG["audio"]["sr"]
LABELS = {name: i for i, name in enumerate(CFG["classes"])}


def _burst(f0, decay, dur=0.08, sr=SR):
    t = np.arange(int(sr * dur)) / sr
    return np.sin(2 * np.pi * f0 * t) * np.exp(-t * decay)


def tap_signal(seconds, rng, interval=0.6, f0=None, jitter=0.02, sr=SR):
    """Rhythmic taps: near-constant interval (what a trapped human does)."""
    x = np.zeros(int(seconds * sr))
    f0 = f0 or rng.uniform(600, 1400)
    t = rng.uniform(0.1, 0.4)
    while t < seconds - 0.1:
        b = _burst(f0, 60.0) * rng.uniform(0.8, 1.0)
        i = int(t * sr)
        x[i : i + len(b)] += b[: len(x) - i]
        t += interval + rng.normal(0, jitter)
    return x


def settling_signal(seconds, rng, rate_hz=1.5, sr=SR):
    """Aperiodic Poisson impulses, lower and varied pitch (rubble settling)."""
    x = np.zeros(int(seconds * sr))
    t = rng.exponential(1 / rate_hz)
    while t < seconds - 0.1:
        b = _burst(rng.uniform(100, 500), rng.uniform(25, 80), dur=0.12) * rng.uniform(0.3, 1.0)
        i = int(t * sr)
        x[i : i + len(b)] += b[: len(x) - i]
        t += rng.exponential(1 / rate_hz)
    return x


def shout_signal(seconds, rng, sr=SR):
    """Voiced harmonics with syllabic amplitude modulation."""
    t = np.arange(int(seconds * sr)) / sr
    f0 = rng.uniform(180, 320)
    x = sum(np.sin(2 * np.pi * f0 * k * t) / k for k in range(1, 9))
    env = 0.5 * (1 + np.sin(2 * np.pi * rng.uniform(2.0, 4.0) * t))
    return x * env / 4.0


def machinery_signal(seconds, rng, sr=SR):
    """Generator hum (harmonics of 50/60 Hz) + low-passed broadband noise."""
    n = int(seconds * sr)
    t = np.arange(n) / sr
    base = rng.choice([50.0, 60.0])
    hum = sum(np.sin(2 * np.pi * base * k * t + rng.uniform(0, 6.28)) / k for k in range(1, 12))
    b, a = butter(2, 2500 / (sr / 2))
    return 0.5 * hum / 3 + lfilter(b, a, rng.normal(0, 1, n)) * 0.5


def rubble_channel(x, depth_m, alpha, sr=SR):
    """Eq.13 amplitude law A0*exp(-alpha d)/d^2 plus depth-dependent low-pass (rubble damping)."""
    d = max(depth_m, 0.3)
    cutoff = max(300.0, 3500.0 / (1.0 + d))
    b, a = butter(2, cutoff / (sr / 2))
    return lfilter(b, a, x) * np.exp(-alpha * d) / d**2


def mix_at_snr(clean, noise, snr_db):
    """Scale `noise` so 10*log10(P_clean/P_noise) == snr_db, return clean+noise."""
    pc, pn = np.mean(clean**2), np.mean(noise**2)
    if pc < 1e-20 or pn < 1e-20:
        return clean + noise
    return clean + noise * np.sqrt(pc / (pn * 10 ** (snr_db / 10)))


def make_example(label, rng, seconds=None, snr_db=None, depth_m=None):
    """Return (noisy, clean_at_mic, meta). `clean_at_mic` is the source after the rubble channel."""
    s = CFG["synth"]
    seconds = seconds or s["clip_seconds"]
    snr_db = rng.uniform(*s["snr_db_range"]) if snr_db is None else snr_db
    depth_m = rng.uniform(*s["depth_m_range"]) if depth_m is None else depth_m
    n = int(seconds * SR)
    if label == LABELS["tap_knock"]:
        src = tap_signal(seconds, rng, interval=rng.uniform(0.4, 0.9))
    elif label == LABELS["shout"]:
        src = shout_signal(seconds, rng)
    elif label == LABELS["rubble_settling"]:
        src = settling_signal(seconds, rng)
    else:
        src = np.zeros(n)
    clean = rubble_channel(src, depth_m, s["alpha_per_m"])
    noise = machinery_signal(seconds, rng)
    noisy = mix_at_snr(clean, noise, snr_db) if np.any(clean) else noise
    return noisy.astype(np.float64), clean.astype(np.float64), {
        "label": label, "snr_db": snr_db, "depth_m": depth_m
    }
