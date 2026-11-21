import pytest

tf = pytest.importorskip("tensorflow")
from rubble_ear import models


def test_denoiser_shape():
    m = models.build_crnn_denoiser(64)
    assert m.output_shape[-1] == 64


def test_classifier_forward():
    import numpy as np
    m = models.build_fusion_classifier(use_yamnet=False)
    assert m(np.zeros((2, 50, 13), "float32")).shape == (2, 4)


def test_regressor_shape():
    assert models.build_mlp_regressor().output_shape[-1] == 1
