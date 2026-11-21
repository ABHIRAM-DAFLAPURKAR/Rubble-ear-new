import numpy as np

from rubble_ear import features as F


def test_hann_periodic():
    w = F.hann(8)
    assert w[0] == 0 and abs(w[4] - 1) < 1e-12


def test_frame_count():
    assert F.frame_count(399) == 0 and F.frame_count(400) == 1 and F.frame_count(4000) == 23


def test_sine_peak_bin():
    n = np.arange(16000)
    x = np.sin(2 * np.pi * 1000 * n / 16000)
    p = F.stft_power(x)[10]
    assert abs(np.argmax(p) * 16000 / 512 - 1000) <= 16000 / 512


def test_mel_roundtrip_and_monotonic():
    f = np.array([100.0, 1000.0, 4000.0])
    assert np.allclose(F.mel_to_hz(F.hz_to_mel(f)), f)
    assert np.all(np.diff(F.hz_to_mel(np.linspace(0, 8000, 50))) > 0)


def test_filterbank_shape_nonneg():
    fb = F.mel_filterbank()
    assert fb.shape == (64, 257) and fb.min() >= 0 and (fb.sum(1) > 0).all()


def test_logmel_shape_finite():
    lm = F.log_mel(np.random.default_rng(0).normal(size=16000))
    assert lm.shape == (98, 64) and np.isfinite(lm).all()


def test_rms_zcr():
    assert abs(F.rms(np.ones(10)) - 1) < 1e-12
    assert abs(F.zcr(np.array([1, -1, 1, -1.0])) - 1.0) < 1e-12


def test_mfcc_shape():
    assert F.mfcc(np.random.default_rng(1).normal(size=8000)).shape[1] == 13
