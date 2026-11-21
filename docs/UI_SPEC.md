# UI / PWA SPEC (prototype exists; extend, do not redesign)
Screen (mobile-first, dark, ≥44 px targets): header (online/OFFLINE badge + pipeline name) · controls [Start microphone | Demo (simulated) | Stop | Clear map] · status card (label, confidence %, periodicity, range m, vibration RMS; green when conf>0.35) · two spectrograms (raw vs filtered) · proximity map 6×6 m (tap = phone position, "Record reading", ≥2 readings → green circle = estimate).
Behaviours: Demo works with no mic; mic constraints AGC/NS/EC off; errors shown in `role=alert`; state resets on Stop; fully functional offline.
PWA: manifest (standalone, 192/512 icons), SW registered only in production, VERSION bump on release, installable on Chrome/Android; iOS Safari: Add to Home Screen, DeviceMotion permission via click.
Accessibility: aria-labels on canvases, colour not sole signal (text label + %), `prefers-reduced-motion` respected (M8).
Out of scope for prototype: accounts, backend, maps, push notifications.
