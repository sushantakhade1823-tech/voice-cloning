"""Fail-closed integration boundary for a pinned OpenVoice V2 revision."""
from pathlib import Path
from .types import SynthesisOptions
from ..config import settings

def synthesize(sample_path: Path, text: str, output_path: Path, options: SynthesisOptions):
    if not settings.openvoice_root.exists():
        raise RuntimeError("OpenVoice model directory is not mounted")
    try:
        import torch
    except ImportError as exc:
        raise RuntimeError("GPU inference dependencies are not installed") from exc
    raise RuntimeError(
        "Pin a reviewed OpenVoice revision and checkpoints, then complete "
        "app/engines/openvoice.py using that revision's documented API."
    )
