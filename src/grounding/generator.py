from dataclasses import dataclass
from math import isfinite

from src.grounding.store import Excerpt


@dataclass(frozen=True)
class Citation:
    document_id: str
    title: str
    section: str
    source_url: str
    excerpt: str
    is_example: bool


@dataclass(frozen=True)
class Narrative:
    summary: str
    citations: tuple[Citation, ...]
    warnings: tuple[str, ...]


def generate_summary(predicted_mgd: float, excerpts: list[Excerpt]) -> Narrative:
    if not isfinite(predicted_mgd) or predicted_mgd < 0:
        raise ValueError("the summary needs an already calculated, nonnegative forecast")
    lead = f"Calculated daily on-site cooling consumption: {predicted_mgd:.4f} MGD."
    if not excerpts:
        return Narrative(
            lead + " No indexed regulatory excerpt matches this location. "
            "Local permit and allocation review is required.",
            (),
            ("no_regulatory_grounding",),
        )
    citations = tuple(
        Citation(
            document_id=excerpt.chunk.permit.document_id,
            title=excerpt.chunk.permit.title,
            section=excerpt.chunk.permit.section,
            source_url=excerpt.chunk.permit.source_url,
            excerpt=excerpt.chunk.text,
            is_example=excerpt.chunk.permit.is_example,
        )
        for excerpt in excerpts
    )
    # Extractive text only. Permit numbers and caps are quoted, never parsed or compared.
    paragraphs = [
        lead,
        "Retrieved excerpts for review; applicability is not a compliance decision.",
    ]
    for citation in citations:
        label = "Example document" if citation.is_example else "Document"
        paragraphs.append(
            f'{label}: {citation.title}, section {citation.section}: "{citation.excerpt}"'
        )
    warnings = (
        ("example_permits_not_regulatory_evidence",)
        if any(citation.is_example for citation in citations)
        else ()
    )
    return Narrative("\n\n".join(paragraphs), citations, warnings)
