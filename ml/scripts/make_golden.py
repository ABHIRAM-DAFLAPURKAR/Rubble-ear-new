"""Regenerate parity/golden.json. TS tests compare against it. Run: python ml/scripts/make_golden.py"""
import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from rubble_ear import features as F
from rubble_ear.config import ROOT, load

cfg = load()["audio"]
n = np.arange(4000)
x = 0.5 * np.sin(2 * np.pi * 440 * n / 16000) + 0.25 * np.sin(2 * np.pi * 1250 * n / 16000)
lm = F.log_mel(x)
golden = {
    "signal": "0.5*sin(2pi*440*n/16000)+0.25*sin(2pi*1250*n/16000), n=0..3999",
    "config": cfg, "n_frames": int(lm.shape[0]),
    "log_mel_first3": [[round(float(v), 9) for v in row] for row in lm[:3]],
    "log_mel_mean": round(float(lm.mean()), 9),
    "rms": round(F.rms(x), 9), "zcr": round(F.zcr(x), 9),
}
(ROOT / "parity" / "golden.json").write_text(json.dumps(golden, indent=1))
print("wrote parity/golden.json frames:", golden["n_frames"])
