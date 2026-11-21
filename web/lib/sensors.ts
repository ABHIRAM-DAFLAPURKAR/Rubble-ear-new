/** Accelerometer: Generic Sensor API (Chrome/Android) else DeviceMotion (iOS needs a user-gesture permission).
 * Browsers cap ~50-60 Hz: do not assume more. Prototype only displays vibration RMS. */
export type Stop = () => void;
export async function startVibration(onRms: (v: number) => void): Promise<Stop> {
  const w = window as any;
  const win: number[] = [];
  const push = (m: number) => { win.push(m); if (win.length > 50) win.shift(); onRms(Math.sqrt(win.reduce((s, v) => s + v * v, 0) / win.length)); };
  if (w.Accelerometer) {
    const s = new w.Accelerometer({ frequency: 50 });
    let g = 0;
    s.addEventListener("reading", () => { const m = Math.hypot(s.x, s.y, s.z); g = 0.98 * g + 0.02 * m; push(m - g); });
    s.start();
    return () => s.stop();
  }
  const D = w.DeviceMotionEvent;
  if (D?.requestPermission && (await D.requestPermission()) !== "granted") throw new Error("Motion permission denied");
  const h = (e: DeviceMotionEvent) => { const a = e.accelerationIncludingGravity; if (a) push(Math.hypot(a.x ?? 0, a.y ?? 0, a.z ?? 0) - 9.81); };
  window.addEventListener("devicemotion", h);
  return () => window.removeEventListener("devicemotion", h);
}
