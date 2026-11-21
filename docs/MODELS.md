# MODELS & EQUATIONS (authoritative spec; implement exactly)

## Features (Python = TS, see features.py/features.ts)
Eq1 STFT: X(m,k)=Σₙ x(n)w(n−mH)e^{−j2πkn/N} (win 400 periodic Hann, hop 160, n_fft 512, zero-pad, no centre).
Eq2 mel(f)=2595·log10(1+f/700); 64 triangular un-normalised filters 20–8000 Hz. Feature = ln(mel_power + 1e-6).
Eq3 MFCC cₙ=Σₖ ln(Sₖ)cos[n(k−½)π/K] (orthonormal DCT-II, first 13). Eq4 ZCR, Eq5 RMS, Eq6 spectral centroid.
Extras: onset envelope (rectified spectral flux), periodicity score (max normalised autocorr, lag 0.15–1.5 s), accelerometer RMS/band energy @50 Hz.

## 1. CRNN denoiser (`build_crnn_denoiser`)
Input (T,64,1) sqrt-mel-power → 4×[Conv2D 3×3 (16,16,32,32)+BN+ReLU+MaxPool(1,2)] → Reshape (T,128) → 2×BiGRU(128) → Dense(64, sigmoid) = mask M.
Loss (Eq7): L = 1/(TF) ΣₜΣf (S_clean − M·S_noisy)²; train target = clip(S_clean/S_noisy,0,1) (ideal ratio mask). Adam 1e-3, 15–40 epochs, batch 32, early stop on val loss.
Eval: SI-SDR improvement on held-out recordings. **RNNoise is a comparison baseline, not an initialiser** (different features/architecture; its weights cannot seed this GRU).

## 2. Fusion classifier (`build_fusion_classifier`) — 4 classes
Branch A: MFCC(13)+Δ+ΔΔ sequence → 3×Conv1D(32,k5) → TCN 4 residual blocks dilations 1,2,4,8 (causal) → GAP.
Branch B: YAMNet 1024-d embedding (mean over window) → Dense(128). Concat → Dropout .2 → Softmax.
Eq8 conv y[i]=Σw[k]x[i+k]+b · Eq9 dilated causal y[t]=Σw[k]x[t−d·k] · Eq10 softmax · Eq11 CE loss.
Why two branches: YAMNet hops 0.48 s (semantic, no rhythm); the TCN sees 10 ms frames (rhythm).
Class imbalance: class weights. Augment: SpecAugment (time/freq mask), gain, SNR jitter −10..+10 dB.

## 3. Transfer learning (YAMNet; VGGish as ablation)
Stage A: freeze YAMNet, train head 15–20 epochs. Stage B: unfreeze top ~25% conv layers, lr 1e-5, 10 epochs, with L2-anchor Eq12: L = L_cls + λ‖θ−θ_pre‖² (λ=1e-4).
YAMNet source: TF Hub `google/yamnet/1` (Apache-2.0). For in-browser/offline use, bundle its TF.js weights under `web/public/models/yamnet/` (≈15 MB; if over budget, distil to a small student or drop Branch B — report the accuracy delta).

## 4. Range MLP (`build_mlp_regressor`)
Input 4-d [ln rms, ln centroid, mean log-mel, periodicity] standardised (mu/sd saved in metrics JSON) → Dense64 → Dense32 → Dense1 (range metres). Eq14 forward, Eq15 MSE (use Huber if outliers).
Physical prior Eq13: A(d)=A₀e^{−αd}/d²; `a0`,`alpha` calibrated in the field (M5); synthetic α=0.6/m is an **assumption**.
Output is **range only**. X/Y: `lib/localize.ts` ring-intersection of ≥2 readings from different phone positions: heat(p)=Σᵢ wᵢ·exp(−(‖p−cᵢ‖−dᵢ)²/2σ²).

## 5. Export & budget
Keras → `tensorflowjs_converter --input_format=keras --quantize_float16` (ONNX via tf2onnx is the alternative; pick one per model, record choice). Only TF.js-supported ops (no tf.signal in-model; features are computed in JS). Total models < 10 MB (excluding optional YAMNet), p95 latency < 2 s per 2 s window.

## Metrics definitions
Acc, per-class recall/precision/F1, macro-F1; SI-SDR = 10log10(‖αs‖²/‖αs−ŝ‖²), α=⟨ŝ,s⟩/‖s‖²; MAE_m; latency ms (p50/p95) on named device.
