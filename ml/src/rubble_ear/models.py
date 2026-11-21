"""Keras model builders. TensorFlow imported lazily so core tests run without it."""
from __future__ import annotations


def _tf():
    import tensorflow as tf
    return tf


def build_crnn_denoiser(n_mels=64, n_frames=None):
    """Conv2D x4 (pool on freq only) -> 2x BiGRU(128) -> sigmoid mask (Eq.7). TF.js-safe ops."""
    tf = _tf(); L = tf.keras.layers
    inp = L.Input((n_frames, n_mels, 1))
    x = inp
    for ch in (16, 16, 32, 32):
        x = L.Conv2D(ch, 3, padding="same")(x); x = L.BatchNormalization()(x)
        x = L.ReLU()(x); x = L.MaxPool2D((1, 2))(x)
    x = L.Reshape((-1, (n_mels // 16) * 32))(x)
    for _ in range(2):
        x = L.Bidirectional(L.GRU(128, return_sequences=True))(x)
    mask = L.Dense(n_mels, activation="sigmoid")(x)
    return tf.keras.Model(inp, mask, name="crnn_denoiser")


def _tcn_block(x, filters, dilation, k=3):
    tf = _tf(); L = tf.keras.layers
    y = L.Conv1D(filters, k, padding="causal", dilation_rate=dilation, activation="relu")(x)
    y = L.SpatialDropout1D(0.1)(y)
    y = L.Conv1D(filters, k, padding="causal", dilation_rate=dilation, activation="relu")(y)
    if x.shape[-1] != filters:
        x = L.Conv1D(filters, 1)(x)
    return L.Add()([x, y])


def build_fusion_classifier(n_feat=13, n_classes=4, emb_dim=1024, use_yamnet=True):
    """Branch A: 3x Conv1D + TCN(1,2,4,8) over MFCC/feature sequence (fine rhythm, 10 ms hop).
    Branch B: pooled YAMNet embedding (coarse semantics; YAMNet hop is 0.48 s so it cannot see rhythm)."""
    tf = _tf(); L = tf.keras.layers
    seq = L.Input((None, n_feat), name="feat_seq")
    x = seq
    for _ in range(3):
        x = L.Conv1D(32, 5, padding="same", activation="relu")(x)
    for d in (1, 2, 4, 8):
        x = _tcn_block(x, 32, d)
    x = L.GlobalAveragePooling1D()(x)
    inputs = [seq]
    if use_yamnet:
        emb = L.Input((emb_dim,), name="yamnet_emb")
        e = L.Dense(128, activation="relu")(emb)
        x = L.Concatenate()([x, e]); inputs.append(emb)
    out = L.Dense(n_classes, activation="softmax")(L.Dropout(0.2)(x))
    return tf.keras.Model(inputs, out, name="fusion_classifier")


def build_mlp_regressor(n_in=4, n_out=1):
    """Eq.14. n_out=1 (range in metres). X/Y come from multilateration (web/lib/localize.ts)."""
    tf = _tf(); L = tf.keras.layers
    inp = L.Input((n_in,))
    x = L.Dense(64, activation="relu")(inp); x = L.Dense(32, activation="relu")(x)
    return tf.keras.Model(inp, L.Dense(n_out)(x), name="mlp_range")
