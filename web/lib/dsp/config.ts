// MUST mirror ml/configs/default.yaml `audio:` block. Parity test enforces equality with parity/golden.json.
export const AUDIO = {
  sr: 16000, win: 400, hop: 160, nFft: 512, nMels: 64, fmin: 20, fmax: 8000, eps: 1e-6,
} as const;
export const IMU_SR = 50;
