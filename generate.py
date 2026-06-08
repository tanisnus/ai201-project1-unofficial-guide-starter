"""
generate.py
Retrieves relevant chunks, generates a grounded answer via Groq, and attaches
sources programmatically (not left to the LLM).
Run embed.py first. Requires GROQ_API_KEY in .env.
"""

import os
import re
from dataclasses import dataclass, field

from dotenv import load_dotenv
from groq import Groq

from retrieve import DEFAULT_TOP_K, retrieve

load_dotenv()

GROQ_MODEL = "llama-3.3-70b-versatile"
# Chroma cosine distance: lower = more similar. Drop chunks above this threshold.
RELEVANCE_THRESHOLD = 0.48

REFUSAL_MESSAGE = (
    "I don't have enough information in my sources to answer that question. "
    "This assistant only answers questions about California community college "
    "to UC transfer pathways using its indexed documents."
)

SYSTEM_PROMPT = """You are a UC community college transfer advisor.

You MUST answer using ONLY the context passages provided in the user message.

STRICT RULES — follow exactly:
1. Use ONLY facts explicitly stated in the passages. Do NOT use outside knowledge, training data, or assumptions.
2. If the passages do not contain enough information to answer the question, respond with EXACTLY this sentence and nothing else:
   "I don't have enough information in my sources to answer that question."
3. Do NOT guess, extrapolate, or fill gaps with general knowledge.
4. Do NOT use numbered bracket citations like [1] or [2] in your answer. Refer to sources by name in plain text when helpful (e.g. "according to UC Admissions").
5. When official UC sources and unofficial forum posts conflict, state both perspectives and note which is official vs. student-reported.
6. Do NOT include a sources list, bibliography, or URLs at the end — the system appends sources automatically.
7. Keep answers concise and practical for community college students planning a UC transfer."""


@dataclass
class RetrievedChunk:
    index: int  # retrieval rank (1–k), used for debug display only
    text: str
    source: str
    url: str
    category: str
    filename: str
    distance: float
    source_id: int = 0  # deduplicated source number, matches Sources list


@dataclass
class SourceAttribution:
    index: int
    source: str
    url: str
    filename: str
    category: str


@dataclass
class GenerationResult:
    query: str
    answer: str
    answer_body: str
    refused: bool
    sources: list[SourceAttribution] = field(default_factory=list)
    chunks: list[RetrievedChunk] = field(default_factory=list)


def _parse_retrieval(results: dict) -> list[RetrievedChunk]:
    chunks = []
    for i, (text, metadata, distance) in enumerate(zip(
        results["documents"][0],
        results["metadatas"][0],
        results["distances"][0],
    )):
        chunks.append(RetrievedChunk(
            index=i + 1,
            text=text,
            source=metadata["source"],
            url=metadata.get("url", ""),
            category=metadata["category"],
            filename=metadata["filename"],
            distance=distance,
        ))
    return chunks


def _filter_relevant_chunks(chunks: list[RetrievedChunk]) -> list[RetrievedChunk]:
    return [c for c in chunks if c.distance <= RELEVANCE_THRESHOLD]


def _build_source_attributions(chunks: list[RetrievedChunk]) -> list[SourceAttribution]:
    """Deduplicate sources programmatically from retrieved chunk metadata."""
    seen: set[tuple[str, str]] = set()
    sources: list[SourceAttribution] = []

    for chunk in chunks:
        key = (chunk.source, chunk.url)
        if key in seen:
            continue
        seen.add(key)
        sources.append(SourceAttribution(
            index=len(sources) + 1,
            source=chunk.source,
            url=chunk.url,
            filename=chunk.filename,
            category=chunk.category,
        ))

    return sources


def _assign_source_ids(chunks: list[RetrievedChunk]) -> list[SourceAttribution]:
    """Build deduplicated source list and tag each chunk with its source_id."""
    sources = _build_source_attributions(chunks)
    key_to_id = {(s.source, s.url): s.index for s in sources}
    for chunk in chunks:
        chunk.source_id = key_to_id[(chunk.source, chunk.url)]
    return sources


def _build_context_block(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for chunk in chunks:
        header = f"[{chunk.source_id}] Source: {chunk.source}"
        if chunk.url:
            header += f" | {chunk.url}"
        header += f" | Category: {chunk.category}"
        parts.append(f"{header}\n{chunk.text}")
    return "\n\n---\n\n".join(parts)


def _strip_bracket_citations(text: str) -> str:
    """Remove any [n] citations the LLM may still produce."""
    text = re.sub(r"\s*\[\d+\]", "", text)
    text = re.sub(r"\s{2,}", " ", text)
    text = re.sub(r"\s+,", ",", text)
    text = re.sub(r",\s*,", ",", text)
    text = re.sub(r"\s+\.", ".", text)
    return text.strip()


def _format_sources_block(sources: list[SourceAttribution]) -> str:
    if not sources:
        return ""

    lines = ["\n\n---\n**Sources:**"]
    for source in sources:
        if source.url:
            lines.append(f"- [{source.index}] {source.source} — {source.url}")
        else:
            lines.append(f"- [{source.index}] {source.source} (`{source.filename}`)")
    return "\n".join(lines)


def _call_llm(query: str, context: str) -> str:
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY not set. Copy .env.example to .env and add your key."
        )

    client = Groq(api_key=api_key)
    user_message = (
        f"Context passages:\n\n{context}\n\n"
        f"Question: {query}\n\n"
        "Answer using only the passages above. Do not use numbered bracket citations like [1] or [2]."
    )

    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content.strip()


def _is_refusal(text: str) -> bool:
    return "I don't have enough information in my sources to answer that question." in text


def answer_query(query: str, top_k: int = DEFAULT_TOP_K) -> GenerationResult:
    """
    Full RAG pipeline: retrieve → filter → generate → attach sources.
    Sources are always appended by code, never trusted from the LLM.
    """
    query = query.strip()
    if not query:
        return GenerationResult(
            query=query,
            answer="Please enter a question about UC transfer from a California community college.",
            answer_body="",
            refused=True,
            sources=[],
            chunks=[],
        )

    raw_results = retrieve(query, top_k=top_k)
    all_chunks = _parse_retrieval(raw_results)
    relevant_chunks = _filter_relevant_chunks(all_chunks)

    if not relevant_chunks:
        sources = _assign_source_ids(all_chunks)
        return GenerationResult(
            query=query,
            answer=REFUSAL_MESSAGE,
            answer_body=REFUSAL_MESSAGE,
            refused=True,
            sources=sources,
            chunks=all_chunks,
        )

    sources = _assign_source_ids(relevant_chunks)
    context = _build_context_block(relevant_chunks)
    answer_body = _call_llm(query, context)

    if _is_refusal(answer_body):
        return GenerationResult(
            query=query,
            answer=REFUSAL_MESSAGE,
            answer_body=answer_body,
            refused=True,
            sources=sources,
            chunks=relevant_chunks,
        )

    answer_body = _strip_bracket_citations(answer_body)

    # Programmatically guarantee source attribution in the final output.
    answer = answer_body + _format_sources_block(sources)

    return GenerationResult(
        query=query,
        answer=answer,
        answer_body=answer_body,
        refused=False,
        sources=sources,
        chunks=relevant_chunks,
    )


def format_chunks_for_display(chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return "_No chunks retrieved._"

    parts = []
    for chunk in chunks:
        parts.append(
            f"**Chunk {chunk.index}** | Source **[{chunk.source_id}]** | "
            f"distance={chunk.distance:.3f} | {chunk.source} (`{chunk.filename}`)\n\n"
            f"{chunk.text}"
        )
    return "\n\n---\n\n".join(parts)


if __name__ == "__main__":
    import sys

    test_query = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "What is the minimum GPA a California resident needs to transfer to a UC?"
    )

    print(f"Query: {test_query}\n")
    result = answer_query(test_query)
    print(result.answer)
    if result.refused:
        print("\n(refused — no grounded answer generated)")
