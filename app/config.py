from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    voice_engine: str = "mock"
    data_dir: Path = Path("/app/data")
    max_upload_mb: int = 25
    max_text_chars: int = 5000
    openvoice_root: Path = Path("/models/openvoice")
    openvoice_device: str = "cuda"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
settings.data_dir.mkdir(parents=True, exist_ok=True)
(settings.data_dir / "uploads").mkdir(exist_ok=True)
(settings.data_dir / "outputs").mkdir(exist_ok=True)
