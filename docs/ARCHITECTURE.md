# ARCHITECTURE
mic (48k/16k) ─AudioWorklet→ resample 16k → ring buffer (2 s) ─┐
accel (50 Hz, Generic Sensor | DeviceMotion) ─ band energy ────┤
                                                              ▼
              log-mel (lib/dsp) → Pipeline.process() → Result{raw,filtered,label,conf,rangeM}
                                   │ HeuristicPipeline (fallback, no models)
                                   └ TfjsPipeline (denoiser→classifier→range) in Web Worker
Result → Spectrogram canvases · confidence meter · "Record reading" → lib/localize ring heatmap → Canvas (Three.js later)
Offline: Service Worker (cache-first assets/models, network-first navigation w/ cache fallback). No runtime network calls.
Files: web/app/page.tsx (UI shell) · web/lib/{pipeline,tfjsPipeline,localize,sensors,demo}.ts · web/lib/dsp/* · web/components/* · web/public/{sw.js,manifest.webmanifest,worklets,models}.
