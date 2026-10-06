# RAG Notes — Basics to Chunking

## 1. What is RAG?

**RAG = Retrieval-Augmented Generation**

RAG allows an LLM to answer using **external knowledge** instead of relying only on what it learned during training.

### Basic flow

```text
User Question
    ↓
Retrieve relevant information
    ↓
Add retrieved information to the prompt
    ↓
LLM generates the answer
```

Example:

If a RAG system contains the QuizMB PRD and the user asks:

> Who controls the leaderboard?

The system first retrieves the relevant section from the PRD, then gives it to the LLM so the answer is grounded in the document.

---

## 2. Two Major Parts of RAG

### A. Indexing

Indexing prepares knowledge **before users ask questions**.

```text
Documents
→ Load
→ Clean
→ Chunk
→ Add Metadata
→ Create Embeddings
→ Store in Search / Vector Index
```

### B. Retrieval

Retrieval happens when a user asks a question.

```text
User Question
→ Search indexed knowledge
→ Retrieve relevant chunks
→ Give chunks + question to LLM
→ Generate answer
```

A useful distinction:

- **Indexing** = prepare knowledge
- **Retrieval** = find useful knowledge

---

# 3. Indexing

Indexing means:

> Preparing data so that it can be searched efficiently later.

Instead of repeatedly reading an entire PDF, website, or database, the system processes the data once and stores searchable representations.

---

# 4. Step 1 — Document Loading

Loading means:

> Taking information from a source and bringing its content into the RAG application.

Possible sources:

- PDF
- TXT / Markdown
- Word documents
- Web pages
- APIs
- Databases
- Google Drive
- Notion
- Support tickets

Example:

```text
quizmb_prd.pdf
    ↓
PDF Loader
    ↓
Extracted text
```

At this stage, we are **not creating embeddings yet**.

### Important distinction

```text
Loading:
File → Text

Embedding:
Text → Vector
```

Loaders often return:

```python
{
    "text": "The host controls the leaderboard.",
    "metadata": {
        "source": "quizmb_prd.pdf",
        "page": 14
    }
}
```

---

# 5. Step 2 — Cleaning

Raw text can contain noise such as:

- repeated headers
- repeated footers
- page numbers
- unnecessary spaces
- broken line breaks
- navigation text
- HTML noise
- duplicates
- encoding problems

Example:

### Before cleaning

```text
QuizMB Product Requirement Document
Page 14

The host controls the
leaderboard.

www.quizmb.com
```

### After cleaning

```text
The host controls the leaderboard.
```

### Why cleaning matters

Bad text produces bad chunks, which can reduce retrieval quality.

But:

> Do not over-clean.

Important information such as API paths, error codes, IDs, headings, and technical syntax should usually be preserved.

---

# 6. Step 3 — Chunking

Chunking means:

> Breaking a large document into smaller pieces that can be retrieved independently.

Instead of:

```text
50-page document → 1 embedding
```

we usually do:

```text
Document
→ Chunk 1
→ Chunk 2
→ Chunk 3
→ ...
```

Each chunk gets its own embedding.

---

# 7. Why Chunking Matters

Chunking has a major effect on RAG quality.

Bad split:

```text
Chunk 1:
The access token expires after

Chunk 2:
24 hours and must then be refreshed.
```

Better chunk:

```text
The access token expires after 24 hours and must then be refreshed.
```

The goal is to create chunks that are:

1. **Coherent** — one main idea
2. **Complete** — enough information to understand it
3. **Focused** — small enough for precise retrieval
4. **Independent** — understandable without the entire document

---

# 8. Chunk Size

There is **no universal best chunk size**.

### Smaller chunks

Advantages:

- precise retrieval
- focused embeddings

Disadvantages:

- less context
- more chunks
- information may get fragmented

### Larger chunks

Advantages:

- more surrounding context
- fewer chunks

Disadvantages:

- less precise retrieval
- unrelated information may be included
- more tokens sent to the LLM

Main trade-off:

```text
Smaller chunks → Precision ↑  Context ↓

Larger chunks  → Context ↑    Precision ↓
```

Chunk size should be tested based on:

- your documents
- user questions
- embedding model
- retrieval method
- downstream LLM usage

---

# 9. Chunk Overlap

Overlap repeats some text between neighboring chunks.

Example:

```text
Chunk 1:
A B C D E

Chunk 2:
D E F G H
```

`D E` is the overlap.

### Why use overlap?

It helps prevent important information from being lost at chunk boundaries.

### Too much overlap causes

- duplicate information
- more embeddings
- more storage
- repeated retrieval results

Overlap should therefore be treated as a tunable parameter, not a fixed rule.

---

# 10. Main Chunking Strategies

## 10.1 Fixed-Size Chunking

Split after a fixed number of tokens or characters.

Example:

```python
chunk_size = 500
chunk_overlap = 50
```

### Pros

- easy
- fast
- predictable
- useful baseline

### Cons

- ignores meaning
- may cut sentences or concepts in the wrong place

### Use when

Starting a RAG prototype or building a simple baseline.

### Real-life example

Imagine indexing thousands of short customer-support messages. Because the messages are already fairly small and similar in size, splitting them into fixed chunks of around a few hundred tokens can be a simple and effective baseline.

---

## 10.2 Sentence / Paragraph Chunking

Split at natural language boundaries.

```text
Paragraph 1 → Chunk
Paragraph 2 → Chunk
Paragraph 3 → Chunk
```

### Pros

- preserves natural meaning
- avoids cutting sentences

### Cons

Paragraphs can have very different sizes.

### Good for

- articles
- blogs
- books
- documentation
- normal prose

Usually combined with a maximum size limit.

### Real-life example

Imagine indexing a collection of news articles. Each paragraph usually discusses one part of the story, so keeping paragraphs intact often creates chunks that are naturally meaningful.

---

## 10.3 Recursive Chunking

Try larger natural boundaries first, then progressively smaller ones.

Conceptually:

```text
Section
  ↓ if too large
Paragraph
  ↓ if too large
Sentence
  ↓ if too large
Word / token boundary
```

### Advantages

Combines:

- size control
- natural boundaries

### Good for

- Markdown
- documentation
- articles
- ordinary PDFs
- general-purpose RAG

A strong default for a first real RAG system.

### Real-life example

Imagine indexing a long employee handbook. A section such as “Leave Policy” may be too large, so the chunker first tries to split it by paragraphs. If a paragraph is still too large, it splits by sentences. This keeps the text natural while still controlling chunk size.

---

## 10.4 Structure-Aware Chunking

Use the existing document structure.

Example:

```markdown
# Authentication
## Login
## Password Reset

# Quiz Session
## Leaderboard
```

Instead of ignoring the headings, the chunker uses them when deciding boundaries.

### Useful structures

- headings
- subsections
- lists
- tables
- code blocks
- chapters
- HTML structure

### Good for

- technical docs
- Markdown
- HTML
- legal documents
- manuals
- research papers
- structured PDFs

### Real-life example

Imagine indexing a software manual with headings such as “Installation”, “Authentication”, “Billing”, and “Troubleshooting”. Keeping each heading together with its content makes retrieval much more meaningful than cutting the manual every fixed number of tokens.

Important rule:

> If useful structure already exists in the document, do not throw it away.

---

## 10.5 Semantic Chunking

Split when the **meaning or topic changes**, rather than after a fixed number of tokens.

Conceptually:

```text
Sentence embeddings
      ↓
Compare semantic similarity
      ↓
Large meaning change?
      ↓
Create chunk boundary
```

Example:

```text
Redis discussion
Redis discussion
Redis discussion
    ↓ topic changes
PostgreSQL discussion
PostgreSQL discussion
```

### Pros

Can create semantically coherent chunks.

### Cons

- more computation
- extra embeddings
- additional tuning
- not guaranteed to outperform simpler approaches

Important lesson:

> More advanced does not automatically mean better.

Use evaluation before adding this complexity.

### Real-life example

Imagine indexing a long interview transcript. The first ten minutes discuss the guest's childhood, then the conversation shifts to career, then business, then investing. Semantic chunking can create boundaries when the topic changes rather than cutting every fixed number of tokens.

---

## 10.6 Hierarchical / Parent-Child Chunking

Hierarchical chunking keeps a relationship between **larger chunks (parents)** and **smaller chunks (children)**.

Example:

```text
Employee Benefits Guide            ← Parent
│
├── Health Insurance               ← Child
├── Dental Insurance               ← Child
├── Paid Leave                     ← Child
└── Retirement Benefits            ← Child
```

The smaller **child chunks** are useful for precise retrieval because they focus on one specific topic.

The larger **parent chunk** preserves more surrounding context.

A common flow is:

```text
User Question
→ Search small child chunks
→ Find the most relevant child
→ Retrieve its parent
→ Give richer context to the LLM
```

Example:

A user asks:

> How many paid leave days do employees receive?

The retriever may match the small **Paid Leave** child chunk. The system can then fetch its larger parent section so the LLM receives the exact answer plus the surrounding policy context.

The easiest way to remember it is:

> **Search small, answer with more context.**

This introduces an important idea:

> The best unit for retrieval does not have to be the same unit given to the LLM.

This pattern is also called **small-to-big retrieval** or **parent-child retrieval**.

### Real-life example

A medical handbook may contain a parent section called **Diabetes Management** with child chunks for medication, diet, exercise, monitoring, and complications. A precise question can retrieve one child, while the parent provides broader context when needed.

---

## 10.7 Contextual Chunking

A chunk may lose meaning when separated from the full document.

Bad standalone chunk:

```text
Revenue increased by 18%.
```

Better:

```text
This section is from ACME's 2025 annual report
and discusses European subscription revenue.

Revenue increased by 18%.
```

Additional context is attached before indexing so the chunk is easier to retrieve correctly.

### Useful for

- long reports
- financial documents
- documents with many references like “it”, “this”, or “previous year”
- highly context-dependent text

### Trade-off

Better context can require additional preprocessing and model cost.

### Real-life example

Imagine indexing annual financial reports. A sentence such as “Revenue increased by 18%” is ambiguous by itself. Adding context such as the company name, reporting period, and business segment before embedding makes the chunk easier to retrieve correctly.

---

# 11. Choosing a Chunking Strategy

Use these as practical starting points:

- **Plain text** → start with **recursive chunking**
- **Markdown documents** → use **structure-aware + recursive chunking**
- **Blogs and articles** → use **sentence/paragraph chunking with a size limit**
- **PDFs** → prefer **layout-aware or structure-aware chunking**
- **Technical documentation** → use **heading-aware chunking**
- **Code** → use **language-aware or AST-aware chunking**
- **Long reports** → consider **hierarchical / parent-child** or **contextual chunking**
- **First RAG prototype** → start with **fixed-size or recursive chunking** as a baseline

These are starting points, not strict rules.

---

# 12. Chunking Must Match User Questions

Chunking should consider not only the document, but also the questions users will ask.

### Narrow questions

> How long is the OTP valid?

Smaller focused chunks may work well.

### Broad questions

> Explain the complete authentication architecture.

Larger chunks, hierarchical retrieval, or parent expansion may work better.

Therefore:

```text
Good chunking =
Document structure
+ Expected questions
+ Retrieval behavior
+ LLM context needs
```

---

# 13. Do Not Break Atomic Information

Try to keep related information together.

Examples:

- heading + paragraph
- question + answer
- table header + table rows
- function signature + relevant body
- definition + explanation
- API endpoint + description

---

# 14. Metadata

Store useful information alongside chunks.

Example:

```python
{
    "text": "The host controls the leaderboard.",
    "metadata": {
        "project": "QuizMB",
        "document": "prd.md",
        "section": "Live Session",
        "subsection": "Leaderboard",
        "chunk_index": 14
    }
}
```

Metadata later helps with:

- filtering
- citations
- source tracking
- parent retrieval
- neighboring chunk retrieval

---

# 15. How to Find the Best Chunking Setup

Do not assume:

```text
500 tokens = best
```

Instead, create realistic questions and test different configurations.

Example:

```text
Experiment A → 256-token recursive
Experiment B → 512-token recursive
Experiment C → structure-aware
Experiment D → semantic
```

Then measure whether the correct evidence appears in the retrieved results.

Useful evaluation concepts we will learn later:

- Recall@K
- Precision@K
- MRR
- answer correctness
- faithfulness

The best chunking strategy is discovered through **evaluation**, not guessing.

---

# Quick Revision

## RAG

```text
Retrieve external knowledge
→ give it to LLM
→ generate grounded answer
```

## Indexing

```text
Load
→ Clean
→ Chunk
→ Metadata
→ Embeddings
→ Store
```

## Loading

```text
Source → usable text
```

## Cleaning

```text
Raw text → remove noise → useful text
```

## Chunking

```text
Large document → smaller searchable units
```

### Main chunking strategies

1. Fixed-size
2. Sentence / paragraph
3. Recursive
4. Structure-aware
5. Semantic
6. Hierarchical
7. Contextual

### Core chunking trade-off

```text
Precision ↔ Context
```

### Four questions to ask about every chunk

- Is it **coherent**?
- Is it **complete**?
- Is it **focused**?
- Can it **stand alone**?

---

## One-Sentence Mental Model

> **RAG indexing prepares knowledge for retrieval, and good chunking divides that knowledge into meaningful, searchable pieces without losing the context needed to answer questions.**
