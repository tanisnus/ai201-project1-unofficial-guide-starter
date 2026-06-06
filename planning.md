# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

<!-- What domain did you choose? Why is this knowledge valuable and hard to find through official channels? -->

Transfer pathway from community colleges, CA CCC, to 4-year universities, UC/CSU.

Having an accurate information on transfer pathway is crucial because taking one wrong step can prevent students from being admitted to 4-year universities. This knowledge is also valuable in financial and timing perspective because being unaware of what set of courses to take can eventually lead to loss of financial aid and spending more time than necessary at a community college.

This domain can be challenging for community college students to navigate because requirements can differ, depending on various factors such as major requirements, general education, sepcific school requirements, and units requirements. Additionally, transfer requirements often change each year, which can possibliy creat confusion amongs transfer students. Some universities official website also have outdated transfer requirements. 


---

## Documents

<!-- List your specific sources: URLs, subreddit names, forum threads, or file descriptions.
     Aim for at least 10 sources that together cover different subtopics or perspectives within your domain. -->

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | r/uctransfer (subreddit) | Unofficial: day-to-day transfer Q&A, admit results, real timelines | https://www.reddit.com/r/uctransfer/ |
| 2 | r/CollegeTransfer (subreddit) | Unofficial: general transfer advice beyond just UC | https://www.reddit.com/r/CollegeTransfer/ |
| 3 | r/ApplyingToCollege (transfer posts) | Unofficial: essays, application strategy, decision threads | https://www.reddit.com/r/ApplyingToCollege/ |
| 4 | College Confidential — UC Transfer FAQs Part 1 | Unofficial curated FAQ: TAG, IGETC, TAP programs, unit caps | https://talk.collegeconfidential.com/t/uc-transfer-faqs-part-1/1996661 |
| 5 | College Confidential — UC Transfers board | Unofficial forum threads: rescinded admits, GPA by major, P/NP | https://talk.collegeconfidential.com/c/transfer-students/uc-transfers/76 |
| 6 | College Confidential — "Is TAG 100% guaranteed?" thread | Unofficial: why TAGs get revoked (missing transcripts, unmet conditions) | https://talk.collegeconfidential.com/t/do-all-students-that-get-their-tag-approved-have-a-100-chance-of-being-admitted/1345277 |
| 7 | UC Davis student TAG blog | First-person walkthrough of the TAG process and pitfalls | https://www.ucdavis.edu/admissions/blog/transfer-admission-guarantee-guide-attend-your-dream-school |
| 8 | Edvisorly — "What is an Articulation Agreement?" | Unofficial guide: plain-English explanation of how credits transfer | https://www.edvisorly.com/student-guides/what-is-an-articulation-agreement |
| 9 | ASSIST.org | Official: which CC courses satisfy major + GE requirements | https://assist.org/ |
| 10 | UC TAG matrix (2026–27) | Official: exact GPA, unit, and deadline requirements per campus | https://admission.universityofcalifornia.edu/_assets/files/transfer-requirements/uc-tag-matrix_2026-2027.pdf |
| 11 | UC Transfer Requirements page | Official: junior standing, 7-course pattern, min GPA (2.4 res / 2.8 nonres) | https://admission.universityofcalifornia.edu/admission-requirements/transfer-requirements/uc-transfer-programs/transfer-admission-guarantee-tag.html |
| 12 | UC Transfer Application Guide (PDF) | Official: importing TAP coursework, TAU, deadlines | https://admission.universityofcalifornia.edu/_assets/files/how-to-apply/application-guide-transfer-applicants.pdf |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
