# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

<!-- What topic or category of knowledge does your system cover?
     Why is this knowledge valuable, and why is it hard to find through official channels?
     Example: "Student reviews of CS professors at [university] — useful because official
     course descriptions don't reflect teaching style, exam difficulty, or workload." -->

Transfer pathway from California community colleges (CCC) to 4-year universities, especially the UC system.

Having accurate information on transfer pathways is crucial because one wrong step can prevent admission to a 4-year university. This knowledge is also valuable from a financial and timing perspective — not knowing which courses to take can lead to loss of financial aid and extra time at community college.

This domain is hard to navigate because requirements differ by major, general education path, campus, and unit minimums. Transfer requirements also change yearly, which creates confusion. Official university websites can be outdated, while student forums contain useful but inconsistent advice — making a grounded RAG system valuable.

---

## Document Sources

<!-- List every source you collected documents from.
     Be specific: include URLs, subreddit names, forum thread titles, or file names.
     Aim for variety — sources that together cover different subtopics or perspectives. -->

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Reddit r/uctransfer & r/CollegeTransfer | Thread | https://www.reddit.com/r/uctransfer/ → `documents/reddit_transfer.txt` |
| 2 | Reddit r/TransferStudents — ASSIST/major prep thread | Thread | https://www.reddit.com/r/TransferStudents/comments/1cgmqsr/where_do_i_look_for_courses_i_need_to_transfer_to/ → `documents/reddit_course_to_transfer.txt` |
| 3 | College Confidential — UC Transfer FAQs Part 1 | FAQ / Guide | https://talk.collegeconfidential.com/t/uc-transfer-faqs-part-1/1996661 → `documents/cc_uc_transfer_faq.txt` |
| 4 | UC Davis student TAG blog | FAQ / Guide | https://www.ucdavis.edu/admissions/blog/transfer-admission-guarantee-guide-attend-your-dream-school → `documents/uc_davis_tag_blog.txt` |
| 5 | Edvisorly — What Is an Articulation Agreement? | FAQ / Guide | https://www.edvisorly.com/student-guides/what-is-an-articulation-agreement → `documents/edvisorly.txt` |
| 6 | UC Admissions — basic transfer requirements | Official | https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/preparing-to-transfer/basic-requirements.html → `documents/uc_transfer_requirements.txt` |
| 7 | UC Admissions — preparing to transfer | Official | https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/preparing-to-transfer/ → `documents/uc_adimission_assist.txt` |
| 8 | UC Admissions — UC transfer programs (TAG) | Official | https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/uc-transfer-programs/ → `documents/uc_admission_tag.txt` |
| 9 | UC TAG matrix (2026–27) | Official | https://admission.universityofcalifornia.edu/_assets/files/transfer-requirements/uc-tag-matrix_2026-2027.pdf → `documents/uc_tag_matrix.pdf` |
| 10 | UC Transfer Application Guide (PDF) | Official | https://admission.universityofcalifornia.edu/_assets/files/how-to-apply/application-guide-transfer-applicants.pdf → `documents/uc_transfer_application_guide.pdf` |

---

## Chunking Strategy

<!-- Describe your chunking approach with enough specificity that someone else could reproduce it.
     Include:
     - Chunk size (characters or tokens) and why that size fits your documents
     - Overlap size and why (or why not) you used overlap
     - Any preprocessing you did before chunking (e.g., stripping HTML, removing headers)
     - What your final chunk count was across all documents -->

Documents are split by category (`official`, `faq`, `thread`) with different chunk sizes:

**Chunk size:**
- **Official** (UC requirements, TAG matrix, application PDF): **2,000 characters**
- **FAQ / Guide** (College Confidential FAQ, Edvisorly, UC Davis blog): **2,800 characters**
- **Thread** (Reddit posts): **1,200 characters**

**Overlap:**
- **300 characters** across all categories. For official docs, overlap helps when a rule and its exception land on either side of a chunk boundary (e.g., minimum GPA in one paragraph, major-specific threshold in the next).

**Why these choices fit your documents:**
- Official documents pack answers into tables, bullet lists, and multi-condition rules — medium chunks keep a full requirement block together.
- FAQ/Guide sources are mostly one question-and-answer block per section — larger chunks keep Q&A pairs intact.
- Reddit threads are shorter posts and replies — smaller chunks reduce unrelated comment noise.

**Preprocessing:** 
`.txt` files have metadata headers stripped by `ingest.py`. Text is cleaned in `chunk.py` (remove invisible Unicode, collapse extra blank lines). PDFs are extracted with `pdfplumber` (multi-column layout handled for the application guide).

**Final chunk count:** **71** chunks across 10 files.

---

## Embedding Model

<!-- Name the embedding model you used and explain your choice.
     Then answer: if you were deploying this system for real users and cost wasn't a constraint,
     what tradeoffs would you weigh in choosing a different model?
     Consider: context length limits, multilingual support, accuracy on domain-specific text,
     latency, and local vs. API-hosted. -->

**Model used:** `all-MiniLM-L6-v2` via sentence-transformers (384-dim vectors, cosine similarity in ChromaDB). Top-k = **5** chunks per query.

**Production tradeoff reflection:**

- **Context length:** MiniLM has a smaller max sequence length; long chunks may be truncated. Alternatives: larger models with longer context windows.
- **Multilingual support:** Optimized for English; cross-language retrieval may be inconsistent. Alternatives: `BAAI/bge-m3`, `multilingual-e5-large`.
- **Domain-specific accuracy:** General-purpose model may miss subtle admissions terminology. Alternatives: `text-embedding-3-large`, `BAAI/bge-large-en-v1.5`.
- **Latency:** MiniLM is fast and runs locally; larger API-hosted models improve quality but add cost and latency.

---

## Grounded Generation

<!-- Explain how your system enforces grounding — how does it prevent the LLM from answering
     beyond the retrieved documents?
     Describe both your system prompt (what instruction you gave the model) and any structural
     choices (e.g., how you formatted the context, whether you filtered low-relevance chunks).
     Do not just say "I told it to use the documents" — show the actual instruction or explain
     the mechanism. -->

**System prompt grounding instruction:**

Grounding is enforced in three layers in `generate.py`:

1. **Structural (pre-LLM):** Top-5 chunks are retrieved, then filtered by cosine distance (`RELEVANCE_THRESHOLD = 0.48`). Chunks above the threshold are dropped. If none remain, the system returns a standardized refusal without calling the LLM.

2. **Prompt (LLM):** The system prompt uses mandatory language (`MUST`, `Do NOT`) and requires an exact refusal sentence when context is insufficient:

   > *"You MUST answer using ONLY the context passages provided in the user message."*
   >
   > *"Use ONLY facts explicitly stated in the passages. Do NOT use outside knowledge, training data, or assumptions."*
   >
   > *"If the passages do not contain enough information to answer the question, respond with EXACTLY this sentence and nothing else: 'I don't have enough information in my sources to answer that question.'"*

   The user message contains only the retrieved passages plus the question — no other context. Temperature is set to 0.1 to reduce hallucination.

3. **Post-generation:** If the LLM emits the refusal phrase, the response is replaced with a standardized `REFUSAL_MESSAGE`. Any stray `[n]` citations are stripped by `_strip_bracket_citations()`.

**How source attribution is surfaced in the response:**

Source attribution is **programmatic**, not left to the LLM. After generation, `generate.py`:

1. Builds a deduplicated source list from retrieved chunk metadata (`source`, `url`, `filename`) via `_build_source_attributions()`
2. Appends a `**Sources:**` block to every answer via `_format_sources_block()` — the LLM is instructed **not** to write its own bibliography (system prompt rule 6)

Example output format:

```
[Answer text in plain prose, may name sources like "according to UC Admissions"]

---
**Sources:**
- [1] UC Admissions — https://admission.universityofcalifornia.edu/...
- [2] College Confidential — UC Transfer FAQs Part 1 — https://talk.collegeconfidential.com/...
```

---

## Evaluation Report

<!-- Run your 5 test questions from planning.md through your system and record the results.
     Be honest — a partially accurate or inaccurate result that you explain well is more
     valuable than a suspiciously perfect result. -->

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | What is the minimum GPA a California resident needs to be eligible to transfer to a UC? | 2.4 (non-residents: 2.8). | According to UC Admissions, the minimum GPA is at least 2.4 in UC-transferable courses for California residents. | Relevant | Accurate |
| 2 | Is a UC TAG a 100% guarantee of admission once approved? | Conditional yes if all contract requirements are met — but admission can be lost if conditions are broken. | States TAG guarantees admission if all campus-specific criteria are met (TAG Matrix, Davis blog); emphasizes matching majors and deadlines but does not clearly address post-approval revocation. | Relevant | Partially accurate |
| 3 | How do I find which community college courses satisfy my major prep for a specific UC campus? | Use ASSIST.org — select your CC, target UC, and major to see articulated/equivalent courses. Also check each campus's major requirements on ASSIST since they can differ from Transfer Pathways. | To find which community college courses satisfy your major prep for a specific UC campus, you can use the ASSIST tool. According to UC Admissions, ASSIST will help you find community college courses that will transfer to UC and satisfy your major preparation requirements. You can also refer to UC's Transfer Pathways, which is a single set of courses you can take to prepare for your major on any of the nine undergraduate campuses. Additionally, you can visit the ASSIST website to see the major preparation coursework expected by each campus.| Relevant | Accurate |
| 4 | How many units do I need to reach junior standing for UC transfer? | 60 semester units or 90 quarter units of transferable coursework. | To reach junior standing for UC transfer, you must complete at least 60 semester or 90 quarter UC-transferable units, according to UC Admissions and the UC TAG Matrix 2026-27. | Relevant | Accurate |
| 5 | Can I use Pass/No Pass (P/NP) grades for courses required to transfer to a UC? | Limited — no more than 14 semester (21 quarter) units of the required 60/90 may be pass/fail; courses generally need a C or better (letter grade). | According to UC Admissions, you need to earn a grade of C or better in each course or a Pass (P) grade if pass is equivalent to a C (2.00). However, it is also stated that no more than 14 semester (21 quarter) units of the 60 semester (90 quarter) units may be taken pass/fail or credit/no credit. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

<!-- Identify at least one question where retrieval or generation did not work as expected.
     Write a specific explanation of *why* it failed, tied to a part of the pipeline.

     "The answer was wrong" is not an explanation.

     "The relevant information was split across a chunk boundary, so retrieval returned
     only half the context — the model didn't have enough to answer correctly" is an explanation.

     "The embedding model treated the professor's nickname as out-of-vocabulary and returned
     results from an unrelated review" is an explanation. -->

**Question that failed:** Is a UC TAG a 100% guarantee of admission once approved?

**What the system returned:** The system cited the UC TAG Matrix and UC Davis TAG blog, described TAG as a guarantee if all campus-specific criteria are met, and emphasized matching majors and application deadlines. It hedged on whether TAG is a "100% guarantee once approved," saying the Davis blog "does not explicitly state" it — without clearly explaining that students must **continue meeting TAG conditions after approval** (GPA, coursework, TAU submission) or admission can be lost.

**Root cause (tied to a specific pipeline stage):**

1. **Corpus / document collection:** Sources conflict. `uc_admission_tag.txt` uses marketing language — *"you have a 100% guaranteed place in your major"* — with no mention of post-approval revocation. The nuance lives in a different file (`uc_davis_tag_blog.txt`: *"uphold their conditions until they transfer"*) and in TAG matrix chunks listing ongoing obligations (TAU deadline, GPA requirements).

2. **Chunking:** The TAG matrix PDF is dense and splits shared criteria, campus-specific rules, and deadline requirements across multiple ~2,000-character chunks. Retrieval often returns a chunk with the word "guarantee" but not the chunk with TAU/ongoing-condition language in the same top-5 set.

3. **Retrieval:** `all-MiniLM-L6-v2` ranks semantically similar "guarantee" language highly. The `uc_admission_tag.txt` marketing chunk and TAG matrix intro chunks outrank the Davis blog chunk that explains post-approval condition upkeep (higher cosine distance).

4. **Generation:** The LLM received conflicting context — official copy saying "100% guaranteed" vs. blog text about upholding conditions — and produced a vague hedge instead of a clear conditional answer grounded in the Davis blog and matrix deadline requirements.

**What you would change to fix it:**

- Add a dedicated official UC page on TAG contract conditions / revocation to the corpus (or scrape the linked TAG detail page behind `uc_admission_tag.txt`).
- Removed duplicate `uc_admission_junior_standing.txt` (same URL as `uc_transfer_requirements.txt`) so top-k slots are not wasted on redundant GPA/unit chunks.
- For TAG matrix PDF, try section-aware chunking (split on headings like "Shared TAG criteria" / "TAU") instead of fixed character splits.
- Optionally boost FAQ/blog chunks at generation time when the query contains "once approved" or "revoked" (metadata filter before LLM call).

---

## Spec Reflection

<!-- Reflect on how planning.md shaped your implementation.
     Answer both questions with at least 2–3 sentences each. -->

**One way the spec helped you during implementation:**

The spec's category-based chunking strategy (official / FAQ / thread with different sizes and 300-char overlap) translated directly into `chunk.py` and gave clear targets when prompting AI tools to implement the pipeline. The architecture diagram and documents table also made it straightforward to wire each stage — `ingest.py` → `chunk.py` → `embed.py` → `retrieve.py` → `generate.py` — without rethinking the overall design. The five evaluation questions in planning.md provided a concrete test suite from day one, which made it easy to judge retrieval and generation quality.

**One way your implementation diverged from the spec, and why:**

The final document corpus diverged from the original 12-source plan. I removed low-quality or outdated forum threads (e.g., the 2012 CC TAG thread) and replaced them with official UC pages (`uc_admission_tag.txt`, `uc_adimission_assist.txt`) after finding the scraped sources were thin or misleading. I also added structural grounding not in the original spec — a cosine-distance relevance filter (`RELEVANCE_THRESHOLD = 0.48`) that refuses before calling the LLM, and programmatic source attribution appended after generation rather than relying on the model to cite documents inline.

---

## AI Usage

<!-- Describe at least 2 specific instances where you used an AI tool during this project.
     For each: what did you give the AI as input, what did it produce, and what did you
     change, override, or direct differently?

     "I used Claude to help me code" is not sufficient.
     "I gave Claude my Chunking Strategy section from planning.md and asked it to implement
     chunk_text(). It returned a function using a fixed character split. I overrode the
     chunk size from 500 to 200 because my documents are short reviews, not long guides." -->

**Instance 1**

- *What I gave the AI:* My Chunking Strategy and Documents table from `planning.md`, the architecture diagram, `requirements.txt`, and sample files from `documents/`. I asked it to implement `ingest.py` and `chunk.py` with category-based chunk sizes and metadata tagging.

- *What it produced:* `ingest.py` with `.txt` header parsing and PDF extraction via `pdfplumber`, plus `chunk.py` with a basic fixed-character sliding window split.

- *What I changed or overrode:* I replaced the generic split with category-specific sizes (official: 2000, FAQ: 2800, thread: 1200 chars) and 300-char overlap from my spec. I added paragraph/sentence boundary snapping in `chunk_text()` so chunks don't cut mid-sentence, and added PDF column-splitting logic in `ingest.py` for the multi-column application guide.

**Instance 2**

- *What I gave the AI:* My `planning.md` grounding requirements, the pipeline diagram, `retrieve.py`, and the assignment's Gradio skeleton. I asked it to wire retrieval to Groq (`llama-3.3-70b-versatile`), enforce grounding in the system prompt, and append sources programmatically — not via the LLM.

- *What it produced:* `generate.py` with a strict `SYSTEM_PROMPT` and `app.py` with a Gradio question/answer interface. The first version instructed the LLM to cite chunks with inline `[1]`, `[2]` brackets.

- *What I changed or overrode:* I added a structural relevance filter (`RELEVANCE_THRESHOLD = 0.48`) that refuses before calling the LLM when retrieval is too weak. I moved source attribution entirely to `_format_sources_block()` so the `**Sources:**` list is always appended by code. I removed inline `[n]` citations from the prompt and stripped any the model still produced, after noticing chunk numbers didn't match the deduplicated source list.
