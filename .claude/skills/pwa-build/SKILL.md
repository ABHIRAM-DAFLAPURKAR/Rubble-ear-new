---
name: pwa-build
description: Use for PWA, offline behaviour, service worker or sensor work.
---
# pwa-build

1. `cd web && npm run build && npm run start` (service worker only runs in production on HTTPS or localhost).
2. DevTools > Application: manifest valid, 192/512 icons, SW activated, cache populated.
3. Offline test: tick Offline, hard reload, press Demo. UI and detection must still work.
4. Mic constraints: echoCancellation/noiseSuppression/autoGainControl all false. iOS DeviceMotion permission only inside a click handler.
5. Bump VERSION in web/public/sw.js on any shell/asset change.
