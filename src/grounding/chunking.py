from dataclasses import dataclass
from math import isfinite
from urllib.parse import urlparse


@dataclass(frozen=True)
class PermitSection:
    document_id: str
    title: str
    section: str
    text: str
    source_url: str
    huc8: tuple[str, ...] = ()
    latitude: float | None = None
    longitude: float | None = None
    radius_km: float | None = None
    is_example: bool = False

    def __post_init__(self) -> None:
        if not all(
            value.strip()
            for value in (self.document_id, self.title, self.section, self.text, self.source_url)
        ):
            raise ValueError("permit sections need an ID, title, section, text, and source URL")
        if urlparse(self.source_url).scheme not in ("https", "http"):
            raise ValueError("permit source must be an HTTP(S) URL")
        if any(len(huc) != 8 or not huc.isascii() or not huc.isdigit() for huc in self.huc8):
            raise ValueError("permit HUCs must be eight digits")
        location = (self.latitude, self.longitude, self.radius_km)
        if any(value is not None for value in location):
            if any(value is None or not isfinite(value) for value in location):
                raise ValueError("coordinate-scoped sections need coordinates and radius_km")
            if not (-90 <= self.latitude <= 90 and -180 <= self.longitude <= 180):
                raise ValueError("invalid permit coordinates")
            if self.radius_km <= 0:
                raise ValueError("permit radius_km must be positive")
        if not self.huc8 and self.latitude is None:
            raise ValueError("permit section needs a HUC or explicit coordinate scope")


@dataclass(frozen=True)
class Chunk:
    chunk_id: str
    permit: PermitSection
    text: str
    start_char: int
    end_char: int


def chunk_section(permit: PermitSection, max_chars: int = 1000, overlap: int = 150) -> list[Chunk]:
    if max_chars < 100 or not 0 <= overlap < max_chars // 2:
        raise ValueError("use max_chars >= 100 and overlap below half the chunk size")
    chunks, start = [], 0
    while start < len(permit.text):
        end = min(start + max_chars, len(permit.text))
        if end < len(permit.text):
            boundary = permit.text.rfind(" ", start + max_chars // 2, end)
            if boundary > start:
                end = boundary
        text = permit.text[start:end]
        chunks.append(
            Chunk(f"{permit.document_id}:{permit.section}:{start}", permit, text, start, end)
        )
        if end == len(permit.text):
            break
        next_start = end - overlap
        if overlap:
            boundary = permit.text.find(" ", next_start, end)
            if boundary >= 0:
                next_start = boundary + 1
        start = max(start + 1, next_start)
    return chunks
