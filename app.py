import streamlit as st
import numpy as np
import io
import wave

st.set_page_config(
    page_title="Universal Musical AI - Master Studio",
    page_icon="🎵",
    layout="wide"
)

# Lightweight & Fast Audio Synthesis Engine (No heavy C-dependencies)
SCALES_HZ = {
    "C (261.63 Hz)": 261.63,
    "C# (277.18 Hz - Male / Gurmat)": 277.18,
    "D (293.66 Hz)": 293.66,
    "D# (311.13 Hz)": 311.13,
    "E (329.63 Hz)": 329.63,
    "F (349.23 Hz)": 349.23,
    "G (392.00 Hz)": 392.00,
    "A (440.00 Hz)": 440.00
}

def generate_ensemble_audio(sa_freq, duration_sec, bpm, use_tanpura, use_surmandal, use_tabla, use_guitar, use_pad):
    sr = 22050
    t = np.linspace(0, duration_sec, int(sr * duration_sec), endpoint=False)
    mix = np.zeros_like(t)

    if use_tanpura:
        tanpura = (
            0.45 * np.sin(2 * np.pi * sa_freq * t) +
            0.30 * np.sin(2 * np.pi * (sa_freq * 1.5) * t) +
            0.20 * np.sin(2 * np.pi * (sa_freq * 2.0) * t) +
            0.15 * np.sin(2 * np.pi * (sa_freq * 0.5) * t)
        )
        mod = 0.85 + 0.15 * np.sin(2 * np.pi * 0.8 * t)
        mix += tanpura * mod * 0.5

    if use_surmandal:
        ratios = [1.0, 1.125, 1.25, 1.5, 1.667, 1.875, 2.0]
        arp = np.zeros_like(t)
        cycle_len = 4.0
        t_mod = np.mod(t, cycle_len)
        for i, r in enumerate(ratios):
            start_t = i * (cycle_len / len(ratios))
            mask = t_mod >= start_t
            env = np.exp(-4.0 * (t_mod[mask] - start_t))
            arp[mask] += 0.25 * np.sin(2 * np.pi * (sa_freq * r) * t[mask]) * env
        mix += arp * 0.5

    if use_tabla:
        beat_interval = 60.0 / bpm
        tabla = np.zeros_like(t)
        beat_times = np.arange(0, duration_sec, beat_interval)
        for idx, bt in enumerate(beat_times):
            mask = (t >= bt) & (t < bt + 0.25)
            dt = t[mask] - bt
            if idx % 4 == 0:
                bayan = np.sin(2 * np.pi * 95 * dt * np.exp(-3 * dt)) * np.exp(-12 * dt)
                dayan = np.sin(2 * np.pi * sa_freq * dt) * np.exp(-25 * dt)
                tabla[mask] += 0.6 * bayan + 0.4 * dayan
            elif idx % 2 == 0:
                dayan = np.sin(2 * np.pi * (sa_freq * 1.5) * dt) * np.exp(-25 * dt)
                tabla[mask] += 0.45 * dayan
            else:
                na = np.sin(2 * np.pi * (sa_freq * 2.0) * dt) * np.exp(-35 * dt)
                tabla[mask] += 0.35 * na
        mix += tabla * 0.6

    if use_guitar:
        guitar = (
            0.3 * np.sin(2 * np.pi * sa_freq * t) +
            0.25 * np.sin(2 * np.pi * (sa_freq * 1.25) * t) +
            0.25 * np.sin(2 * np.pi * (sa_freq * 1.5) * t)
        ) * (0.6 + 0.4 * np.cos(2 * np.pi * (bpm / 60.0) * t))
        mix += guitar * 0.35

    if use_pad:
        pad = (
            0.4 * np.sin(2 * np.pi * (sa_freq * 0.5) * t) +
            0.3 * np.sin(2 * np.pi * sa_freq * t) +
            0.2 * np.sin(2 * np.pi * (sa_freq * 1.5) * t)
        )
        mix += pad * 0.4

    if np.max(np.abs(mix)) > 0:
        mix = mix / np.max(np.abs(mix)) * 0.9
    audio_int16 = np.int16(mix * 32767)
    
    # Use standard wave module instead of scipy
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(audio_int16.tobytes())
    return buf.getvalue()

# UI Layout
st.sidebar.title("🌍 Universal Studio Controls")
selected_scale = st.sidebar.selectbox("Select Tonic Scale (Sa)", list(SCALES_HZ.keys()), index=1)
sa_hz = SCALES_HZ[selected_scale]
bpm = st.sidebar.slider("Tempo / Laya (BPM)", 50, 220, 108)
loop_duration = st.sidebar.selectbox("Practice Loop Length", [15, 30, 60], index=1)

st.sidebar.markdown("---")
st.sidebar.subheader("🎛️ Select Instruments (Up to 5)")
c_tanpura = st.sidebar.checkbox("1. Tanpura Drone", value=True)
c_surmandal = st.sidebar.checkbox("2. Surmandal Arpeggio", value=True)
c_tabla = st.sidebar.checkbox("3. Tabla Rhythm Loop", value=True)
c_guitar = st.sidebar.checkbox("4. Acoustic Guitar", value=False)
c_pad = st.sidebar.checkbox("5. Warm Synth Pad", value=False)

st.title("🎵 Universal Musical AI - Master Studio")
st.write("Click below to generate and play your live multi-instrument accompaniment!")

if st.button("▶️ Generate & Play Live 5-Instrument Accompaniment", type="primary"):
    with st.spinner("Synthesizing acoustic waves..."):
        wav_bytes = generate_ensemble_audio(sa_hz, loop_duration, bpm, c_tanpura, c_surmandal, c_tabla, c_guitar, c_pad)
        st.success(f"Playing Live Ensemble in **{selected_scale}** at **{bpm} BPM**!")
        st.audio(wav_bytes, format="audio/wav", autoplay=True, loop=True)
