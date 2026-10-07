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
