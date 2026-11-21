"use client";
import { useCallback, useEffect, useRef, useState } from "react";
import { SpectrogramCanvas } from "@/components/SpectrogramCanvas";
import { ProximityHeatmap } from "@/components/ProximityHeatmap";
import { AUDIO } from "@/lib/dsp/config";
import { resampleLinear } from "@/lib/dsp/features";
import { demoSeconds } from "@/lib/demo";
import { createPipeline, type Pipeline, type Result } from "@/lib/pipeline";
import type { Reading } from "@/lib/localize";
import { startVibration } from "@/lib/sensors";

const WINDOW_S = 2, TICK_MS = 250;
type Mode = "idle" | "mic" | "demo";

export default function Home() {
  const [mode, setMode] = useState<Mode>("idle");
  const [res, setRes] = useState<Result | null>(null);
  const [vib, setVib] = useState(0);
  const [err, setErr] = useState("");
  const [pipeName, setPipeName] = useState("");
  const [readings, setReadings] = useState<Reading[]>([]);
  const [pos, setPos] = useState<{ x: number; y: number } | null>(null);
  const [online, setOnline] = useState(true);
  const buf = useRef<Float32Array>(new Float32Array(0));
  const pipe = useRef<Pipeline | null>(null);
  const stops = useRef<Array<() => void>>([]);
  const demoT = useRef(0);

  useEffect(() => {
    setOnline(navigator.onLine);
    const on = () => setOnline(true), off = () => setOnline(false);
    window.addEventListener("online", on); window.addEventListener("offline", off);
    createPipeline().then((p) => { pipe.current = p; setPipeName(p.name); });
    return () => { window.removeEventListener("online", on); window.removeEventListener("offline", off); };
  }, []);

  const push = useCallback((chunk: Float32Array) => {
    const max = AUDIO.sr * WINDOW_S, merged = new Float32Array(Math.min(max, buf.current.length + chunk.length));
    const keep = merged.length - chunk.length;
    merged.set(buf.current.subarray(buf.current.length - keep), 0); merged.set(chunk, keep);
    buf.current = merged;
  }, []);

  const stop = useCallback(() => { stops.current.forEach((s) => s()); stops.current = []; buf.current = new Float32Array(0); setMode("idle"); }, []);

  const startMic = async () => {
    setErr("");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false } });
      let ctx: AudioContext;
      try { ctx = new AudioContext({ sampleRate: AUDIO.sr }); } catch { ctx = new AudioContext(); }
      await ctx.audioWorklet.addModule("/worklets/capture.js");
      const src = ctx.createMediaStreamSource(stream), node = new AudioWorkletNode(ctx, "capture");
      node.port.onmessage = (e) => push(resampleLinear(e.data as Float32Array, ctx.sampleRate, AUDIO.sr));
      src.connect(node);
      stops.current.push(() => { stream.getTracks().forEach((t) => t.stop()); ctx.close(); });
      try { stops.current.push(await startVibration(setVib)); } catch { /* vibration optional */ }
      setMode("mic");
    } catch (e) { setErr(String(e)); }
  };
  const startDemo = () => {
    demoT.current = 0;
    const id = setInterval(() => { push(demoSeconds(demoT.current, TICK_MS / 1000, AUDIO.sr, { taps: true, depthM: 1.5 })); demoT.current += TICK_MS / 1000; }, TICK_MS);
    stops.current.push(() => clearInterval(id)); setMode("demo");
  };

  useEffect(() => {
    if (mode === "idle") return;
    const id = setInterval(async () => {
      if (!pipe.current || buf.current.length < AUDIO.sr * 1.0) return;
      setRes(await pipe.current.process(buf.current));
    }, TICK_MS * 2);
    return () => clearInterval(id);
  }, [mode]);

  const addReading = () => {
    if (!pos || !res || res.rangeM == null) return;
    setReadings((r) => [...r, { x: pos.x, y: pos.y, d: res.rangeM!, w: res.confidence }]);
  };

  return (
    <main style={{ maxWidth: 720, margin: "0 auto", padding: 16, display: "grid", gap: 14 }}>
      <header style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h1 style={{ fontSize: 20, margin: 0 }}>RubbleEar</h1>
        <span style={{ fontSize: 12 }}>{online ? "online" : "OFFLINE (fully functional)"} · {pipeName || "loading"}</span>
      </header>
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
        <button onClick={startMic} disabled={mode !== "idle"}>Start microphone</button>
        <button onClick={startDemo} disabled={mode !== "idle"}>Demo (simulated)</button>
        <button onClick={stop} disabled={mode === "idle"}>Stop</button>
        <button onClick={() => setReadings([])}>Clear map</button>
      </div>
      {err && <p role="alert" style={{ color: "#f66" }}>{err}</p>}
      <section style={{ padding: 12, borderRadius: 8, background: res && res.confidence > 0.35 ? "#1b3a1b" : "#1a1a1a" }}>
        <div style={{ fontSize: 28, fontWeight: 700 }} data-testid="label">{res ? res.label.replace("_", " / ") : "—"}</div>
        <div>confidence {res ? (res.confidence * 100).toFixed(0) : 0}% · periodicity {res ? res.periodicity.toFixed(2) : "–"} · range {res?.rangeM != null ? res.rangeM.toFixed(2) + " m" : "–"} · vibration {vib.toFixed(3)}</div>
        <progress max={1} value={res?.confidence ?? 0} style={{ width: "100%" }} />
      </section>
      {res && <>
        <SpectrogramCanvas frames={res.rawLogMel} title="Raw (log-mel)" />
        <SpectrogramCanvas frames={res.filteredLogMel} title="Filtered (noise floor removed)" />
      </>}
      <section>
        <h2 style={{ fontSize: 16 }}>Proximity map (6 m × 6 m)</h2>
        <p style={{ fontSize: 12, opacity: 0.7 }}>1) Tap the map where your phone is placed. 2) Press “Record reading”. 3) Move ≥2 m and repeat: rings intersect at the source (green circle).</p>
        <ProximityHeatmap readings={readings} onPlace={(x, y) => setPos({ x, y })} />
        <button onClick={addReading} disabled={!pos || res?.rangeM == null}>Record reading</button>
      </section>
    </main>
  );
}
