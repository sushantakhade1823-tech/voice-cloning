from typing import Literal
from pydantic import BaseModel, Field, field_validator

class GenerationRequest(BaseModel):
    voice_id: str
    text: str = Field(min_length=1, max_length=5000)
    language: Literal["auto","en","hi","mr"] = "auto"
    emotion: Literal["natural","calm","warm","sad","energetic","powerful","romantic"] = "natural"
    speed: float = Field(1.0, ge=0.7, le=1.3)
    pitch: float = Field(0.0, ge=-6, le=6)
    energy: float = Field(1.0, ge=0.5, le=1.5)
    pause: float = Field(1.0, ge=0.5, le=2.0)
    temperature: float = Field(0.7, ge=0.1, le=1.0)

    @field_validator("text")
    @classmethod
    def clean_text(cls, value):
        value = value.strip()
        if not value:
            raise ValueError("Text cannot be empty")
        return value
