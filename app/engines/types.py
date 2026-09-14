from dataclasses import dataclass

@dataclass
class SynthesisOptions:
    language: str
    emotion: str
    speed: float
    pitch: float
    energy: float
    pause: float
    temperature: float
