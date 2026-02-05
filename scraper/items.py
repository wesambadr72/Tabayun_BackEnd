from dataclasses import dataclass
from typing import Optional


@dataclass
class LegalContentItem:
    title: str
    country: str
    category: Optional[str]
    original_text: str
    source_url: Optional[str] = None

