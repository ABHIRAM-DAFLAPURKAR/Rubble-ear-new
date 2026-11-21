import itertools

import numpy as np

from rubble_ear import data
from rubble_ear import features as F
from rubble_ear import synth as S


def test_mix_at_snr_exact():
    rng = np.random.default_rng(0)
    c, n = rng.normal(size=8000), rng.normal(size=8000)
    for snr in (-10, 0, 10):
        mixed = S.mix_at_snr(c, n, snr)
        noise = mixed - c
        assert abs(10 * np.log10(np.mean(c**2) / np.mean(noise**2)) - snr) < 1e-6


def test_attenuation_monotonic_in_depth():
    x = S.tap_signal(2.0, np.random.default_rng(0))
    e = [np.mean(S.rubble_channel(x, d, 0.6) ** 2) for d in (0.5, 1.0, 2.0, 3.0)]
    assert all(a > b for a, b in itertools.pairwise(e))


def test_make_example_all_labels():
    rng = np.random.default_rng(3)
    for lab in range(4):
        noisy, _clean, meta = S.make_example(lab, rng)
        assert len(noisy) == 4 * 16000 and meta["label"] == lab and np.isfinite(noisy).all()


def test_tap_more_periodic_than_settling():
    rng = np.random.default_rng(7)
    tap = [F.periodicity_score(F.onset_envelope(F.log_mel(S.make_example(0, rng, snr_db=10, depth_m=0.5)[1] + 1e-4 * rng.normal(size=64000)))) for _ in range(5)]
    st = [F.periodicity_score(F.onset_envelope(F.log_mel(S.make_example(2, rng, snr_db=10, depth_m=0.5)[1] + 1e-4 * rng.normal(size=64000)))) for _ in range(5)]
    assert np.mean(tap) > np.mean(st)


def test_dataset_shapes():
    X, y = data.build_classifier_set(8, 0)
    assert X.shape[0] == 8 and X.shape[2] == 13 and set(y) == {0, 1, 2, 3}
    Xr, yr = data.build_range_set(4, 0)
    assert Xr.shape == (4, 4) and yr.shape == (4, 1)
