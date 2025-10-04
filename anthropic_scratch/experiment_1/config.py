from dataclasses import dataclass
from os import getenv

from dotenv import load_dotenv


@dataclass
class Config:
    api_key: str
    model: str
    max_tokens: int
    temperature: float


_ = load_dotenv()

cfg = Config(
    api_key=getenv("ANTHROPIC_API_KEY") or "",
    model=getenv("ANTHROPIC_MODEL") or "claude-3-5-haiku-20241022",
    max_tokens=4096,
    temperature=0.3,
)
