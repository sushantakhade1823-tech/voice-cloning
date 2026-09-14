import math
import wave
from pathlib import Path
from .types import SynthesisOptions

def synthesize(sample_path: Path, text: str, output_path: Path, options: SynthesisOptions):
    rate, duration = 24000, min(3.0, 0.7 + len(text) / 120)
    frames = bytearray()
    for i in range(int(rate * duration)):
        envelope = min(1, i / 1200) * min(1, (rate * duration - i) / 1200)
        value = int(4500 * envelope * math.sin(2 * math.pi * 440 * i / rate))
        frames += value.to_bytes(2, "little", signed=True)
    with wave.open(str(output_path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(frames)
