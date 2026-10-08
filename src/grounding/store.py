import json
from dataclasses import dataclass
from pathlib import Path

import faiss
import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from src.geography import distance_km
from src.grounding.chunking import Chunk, PermitSection, chunk_section


@dataclass(frozen=True)
class Excerpt:
    chunk: Chunk
    score: float


class PermitStore:
    def __init__(self, chunks: list[Chunk]) -> None:
        self.chunks = chunks
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2), max_features=4096, stop_words="english"
        )
        self.index = None
        if chunks:
            vectors = (
                self.vectorizer.fit_transform(
                    [
                        f"{chunk.permit.title} {chunk.permit.section} {chunk.text}"
                        for chunk in chunks
                    ]
                )
                .toarray()
                .astype("float32")
            )
            self.index = faiss.IndexFlatIP(vectors.shape[1])
            self.index.add(vectors)

    @classmethod
    def from_jsonl(cls, path: Path) -> "PermitStore":
        chunks = []
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                if not line.strip():
                    continue
                data = json.loads(line)
                data["huc8"] = tuple(data.get("huc8", ()))
                chunks.extend(chunk_section(PermitSection(**data)))
        return cls(chunks)

    def retrieve(
        self,
        query: str,
        *,
        huc8: str | None = None,
        latitude: float | None = None,
        longitude: float | None = None,
        top_k: int = 3,
    ) -> list[Excerpt]:
        if not 1 <= top_k <= 20:
            raise ValueError("top_k must be between 1 and 20")
        if not self.index:
            return []
        vector = self.vectorizer.transform([query]).toarray().astype("float32")
        if np.linalg.norm(vector) == 0:
            return []
        scores, positions = self.index.search(vector, len(self.chunks))
        matches = []
        for score, position in zip(scores[0], positions[0], strict=True):
            if score <= 0:
                break
            chunk = self.chunks[int(position)]
            permit = chunk.permit
            eligible = huc8 is not None and huc8 in permit.huc8
            if not permit.huc8 and permit.latitude is not None and latitude is not None:
                eligible = (
                    longitude is not None
                    and distance_km(latitude, longitude, permit.latitude, permit.longitude)
                    <= permit.radius_km
                )
            if eligible:
                matches.append(Excerpt(chunk, float(score)))
            if len(matches) == top_k:
                break
        return matches

    def save(self, directory: Path) -> None:
        directory.mkdir(parents=True, exist_ok=True)
        joblib.dump((self.chunks, self.vectorizer), directory / "metadata.joblib")
        if self.index is not None:
            faiss.write_index(self.index, str(directory / "index.faiss"))

    @classmethod
    def load(cls, directory: Path) -> "PermitStore":
        store = cls([])
        store.chunks, store.vectorizer = joblib.load(directory / "metadata.joblib")
        if store.chunks:
            store.index = faiss.read_index(str(directory / "index.faiss"))
            if store.index.ntotal != len(store.chunks):
                raise ValueError("permit index and metadata do not match")
        return store
