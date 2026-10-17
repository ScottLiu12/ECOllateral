from dataclasses import replace
from pathlib import Path

import numpy as np
import pytest
from sklearn.metrics.pairwise import cosine_similarity

from src.grounding.chunking import PermitSection, chunk_section
from src.grounding.store import PermitStore, generate_summary


def section(huc="02070010", **kwargs):
    return PermitSection(
        document_id=huc,
        title="Water withdrawal permit",
        section="IV.B",
        text="Cooling water withdrawals require monthly reporting. The local cap is 0.20 MGD.",
        source_url="https://example.org/permit",
        huc8=(huc,),
        **kwargs,
    )


def test_geography_filtered_before_top_k_and_index_reloads(tmp_path: Path):
    store = PermitStore(chunk_section(section("02070011")) + chunk_section(section()))
    store.save(tmp_path)
    assert {path.name for path in tmp_path.iterdir()} == {"metadata.joblib"}
    store = PermitStore.load(tmp_path)
    excerpts = store.retrieve("cooling water withdrawal", huc8="02070010", top_k=1)
    assert len(excerpts) == 1
    assert excerpts[0].chunk.permit.huc8 == ("02070010",)
    assert store.retrieve("cooling water", huc8="99999999") == []
    assert store.retrieve("zzzxxyyy", huc8="02070010") == []


def test_word_search_ranks_matches_by_cosine_similarity():
    base = section()
    chunks = [
        chunk
        for i, text in enumerate(
            (
                "Cooling water withdrawals require monthly reporting.",
                "Cooling water use is restricted during drought.",
                "The construction noise limit applies at night.",
            )
        )
        for chunk in chunk_section(replace(base, document_id=str(i), text=text))
    ]
    store = PermitStore(chunks)
    query = "cooling water drought"
    expected = cosine_similarity(store.vectors, store.vectorizer.transform([query])).ravel()
    matches = store.retrieve(query, huc8="02070010")
    assert [item.chunk.permit.document_id for item in matches] == [
        chunks[i].permit.document_id for i in np.argsort(expected)[::-1] if expected[i] > 0
    ]
    for item in matches:
        position = chunks.index(item.chunk)
        assert item.score == pytest.approx(expected[position])


def test_chunks_keep_exact_source_offsets():
    permit = section()
    long = PermitSection(**{**permit.__dict__, "text": permit.text * 20})
    chunks = chunk_section(long, max_chars=200, overlap=30)
    assert len(chunks) > 1
    for chunk in chunks:
        assert chunk.text == long.text[chunk.start_char : chunk.end_char]
        assert chunk.permit.section == "IV.B"
        assert len(chunk.text) <= 200


def test_narrative_quotes_caps_without_computing_risk():
    store = PermitStore(chunk_section(section(is_example=True)))
    excerpts = store.retrieve("cooling water", huc8="02070010")
    summary = generate_summary(0.3, excerpts)
    assert "0.3000 MGD" in summary.summary
    assert summary.citations[0].excerpt == section().text
    assert "exceeded" not in summary.summary
    assert "example_permits_not_regulatory_evidence" in summary.warnings
    assert generate_summary(0.3, []).warnings == ("no_regulatory_grounding",)
