import json

import numpy as np

from rubble_ear import features as F
from rubble_ear.config import ROOT


def test_golden_matches_current_python():
    g = json.loads((ROOT / "parity" / "golden.json").read_text())
    n = np.arange(4000)
    x = 0.5 * np.sin(2 * np.pi * 440 * n / 16000) + 0.25 * np.sin(2 * np.pi * 1250 * n / 16000)
    lm = F.log_mel(x)
    assert lm.shape[0] == g["n_frames"]
    assert np.allclose(lm[:3], g["log_mel_first3"], atol=1e-8)
    assert abs(float(lm.mean()) - g["log_mel_mean"]) < 1e-8
