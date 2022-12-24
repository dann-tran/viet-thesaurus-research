from dataclasses import dataclass

from typing import Optional


@dataclass
class VlspEntry:
    headword: str
    pos: str
    definition: str
    synonyms: Optional[str]
    antonyms: Optional[str]
