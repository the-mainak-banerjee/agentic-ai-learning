# Vector Stores / Vector Databases

You already know this flow:

**Load → Clean → Chunk → Embed → Store**

We have covered everything except the final **Store** part.

---

# 1. What is a Vector Store?

A vector store is a system designed to store and search **embeddings**.

Suppose one chunk becomes:

```python
text = "Employees can work remotely three days per week."

embedding = [
    0.17,
    -0.42,
    0.81,
    ...
]
```

We usually want to store more than just the embedding:

```python
{
    "id": "chunk_123",

    "text":
        "Employees can work remotely three days per week.",

    "embedding":
        [0.17, -0.42, 0.81, ...],

    "metadata": {
        "source": "employee_handbook.pdf",
        "section": "Remote Work",
        "page": 18
    }
}
```

So conceptually:

**Vector store =**

> embedding + original chunk + metadata

The embedding is what we search.

The original text is what we later give to the LLM.

The metadata helps us filter and understand where the information came from.

---

# 2. Why can't we just store embeddings in a normal database?

Technically, we **can**.

For example, PostgreSQL with `pgvector` can store vectors and perform vector similarity search. `pgvector` currently supports both exact nearest-neighbor search and approximate indexes such as **HNSW** and **IVFFlat**. [GitHub](https://github.com/pgvector/pgvector?utm_source=chatgpt.com)

The real requirement isn't:

> "I must have a special vector database."

The requirement is:

> **I need a system capable of efficiently storing and searching high-dimensional vectors.**

That could be:

- PostgreSQL + `pgvector`
- Pinecone
- Weaviate
- Qdrant
- another search/vector system

---

# 3. What happens when we store the chunks?

Suppose our indexing pipeline created:

```text
Chunk A → vector A
Chunk B → vector B
Chunk C → vector C
Chunk D → vector D
```

The database stores them.

Conceptually:

```text
Vector Index

Chunk A
[0.17, 0.84, -0.31, ...]

Chunk B
[-0.53, 0.11, 0.72, ...]

Chunk C
[0.61, -0.22, 0.19, ...]

Chunk D
[0.39, 0.52, -0.81, ...]
```

Later the user asks:

> Can I work from home?

We create:

```text
Query embedding
[0.20, 0.79, -0.27, ...]
```

Now the database asks:

> Which stored vectors are closest to this query vector?

That operation is called **vector similarity search** or **nearest-neighbor search**. Weaviate describes vector search exactly this way: compare the query vector with stored object vectors and return the closest matches. [Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/vector-search?utm_source=chatgpt.com)

---

# 4. What does `Top-K` mean?

You will see this constantly in RAG.

Suppose:

```python
top_k = 3
```

It means:

> Return the 3 most similar chunks.

For example:

```text
Query:
"Can I work remotely?"
```

Results:

```text
1. Remote work policy        similarity: 0.94

2. Flexible work policy      similarity: 0.88

3. Office attendance rules   similarity: 0.79
```

Those chunks can then be passed to the LLM.

So:

**Top-K = number of results we want from retrieval.**

---

# 5. But Top-K has a problem

Imagine you say:

```python
top_k = 5
```

The database will usually try to return five closest results.

But what if only two are actually relevant?

You might get:

```text
1. Remote work policy        0.95
2. Hybrid work policy        0.91
3. Employee cafeteria        0.41
4. Office parking            0.36
5. Health insurance          0.32
```

The last three aren't useful.

This teaches us another concept:

## Similarity threshold

Instead of saying only:

> Give me the best five.

you can also say:

> Give me results only if they are sufficiently similar.

Weaviate specifically warns that a vector search always has a "closest" result, even when that result isn't actually relevant, which is why limits, thresholds, and filters are important. [Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/vector-search?utm_source=chatgpt.com)

So retrieval might become:

```text
top_k = 5
minimum_similarity = acceptable threshold
```

Then perhaps only two results are returned.

---

# 6. Exact Nearest Neighbor Search

Let's say you store:

**1,000 vectors.**

One simple solution:

```text
Query vector
     ↓
Compare with vector 1
Compare with vector 2
Compare with vector 3
...
Compare with vector 1000
     ↓
Sort
     ↓
Return closest
```

This is **exact nearest-neighbor search**.

It checks everything.

### Advantage

Very accurate.

### Problem

Imagine:

**100 million vectors.**

Comparing a query against every single vector can become expensive and slow.

That's why vector databases use indexes designed for efficient similarity search.

---

# 7. Approximate Nearest Neighbor — ANN

Instead of checking every vector, the database can search an intelligently organized index.

This is called:

> **Approximate Nearest Neighbor — ANN**

The idea:

```text
Exact search:
Check almost everything
→ maximum recall
→ potentially slower

ANN:
Search promising parts
→ dramatically faster
→ may occasionally miss the mathematically closest result
```

This trade-off is fundamental.

`pgvector`, for example, states that its exact search provides perfect recall, while approximate indexes trade some recall for speed. [GitHub](https://github.com/pgvector/pgvector?utm_source=chatgpt.com)

---

# 8. HNSW

One ANN algorithm you will encounter constantly is:

> **HNSW — Hierarchical Navigable Small World**

You don't need the mathematics now.

The intuition is enough.

Imagine your vectors are cities.

Instead of checking every city one by one, HNSW builds connections between nearby locations.

Conceptually:

```text
             ●
           /   \
      ● —— ● —— ●
      |    |     |
      ● —— ● —— ●
           |
           ●
```

When a query arrives, the algorithm moves through the network toward increasingly similar vectors.

Very roughly:

> start somewhere → jump closer → jump closer → find nearest neighborhood

HNSW is widely used because it offers a strong speed/recall trade-off. In `pgvector`, HNSW generally gives a better query performance trade-off than IVFFlat, though it uses more memory and takes longer to build. [GitHub](https://github.com/pgvector/pgvector?utm_source=chatgpt.com)

You don't need to implement HNSW yourself.

The database handles it.

---

# 9. What about IVFFlat?

Another ANN approach you'll encounter is:

> **IVF / IVFFlat**

The simple intuition:

Instead of one giant collection of vectors, divide them into groups.

For example:

```text
Cluster A
● ● ● ●

Cluster B
      ● ● ●

Cluster C
             ● ● ● ●
```

When the query arrives:

1. Find promising clusters.
2. Search mainly inside those clusters.
3. Avoid scanning everything.

Again, this improves speed.

For learning RAG, remember:

- **HNSW** = graph-based ANN
- **IVF-style indexes** = partition vectors into regions/clusters

No need to go deeper yet.

---

# 10. Metadata Filtering

This is extremely important in real RAG systems.

Imagine your database contains documents for:

```text
Finance department
HR department
Engineering department
Legal department
```

User asks:

> What is our annual leave policy?

Before doing vector search, we might apply:

```python
department = "HR"
```

Now the system searches only relevant HR documents.

Conceptually:

```text
Query
  ↓
Metadata filter
department = HR
  ↓
Vector similarity search
  ↓
Relevant HR chunks
```

Metadata filtering can use things like:

- user ID
- organization ID
- document
- department
- language
- date
- product
- permissions
- category

Weaviate supports combining structured metadata filters with vector search, including pre-filtering before similarity search. [Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/filtering?utm_source=chatgpt.com)

---

# 11. Metadata is also important for security

Imagine a multi-company SaaS RAG application.

Company A uploads:

```text
salary-data.pdf
```

Company B uploads:

```text
financial-plan.pdf
```

If you simply vector-search across everything without tenant filtering, a Company A user might accidentally retrieve Company B's chunks.

So you might enforce:

```python
tenant_id = current_user.company_id
```

before retrieval.

That means metadata filtering isn't only about relevance.

It can also be part of:

> **data isolation and access control.**

---

# 12. Vector Search vs Keyword Search

We touched on this during embeddings.

Vector search is excellent at:

> **meaning**

Example:

```text
Query:
"How can I recover my account?"

Document:
"Use the password reset process."
```

Very useful.

But suppose someone searches:

```text
ERR_AUTH_4017
```

That's an exact error code.

Keyword search may be better.

Similarly:

```text
Invoice ID: INV-72819
```

You probably want exact matching.

This is why many modern RAG systems use:

# Hybrid Search

Hybrid search combines:

**Vector search + keyword search**

Weaviate's current documentation describes hybrid search as running semantic vector search and BM25 keyword search and combining their results into a final ranking. [Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search?utm_source=chatgpt.com)

Conceptually:

```text
                 User Query
                    ↓

          ┌─────────┴─────────┐
          ↓                   ↓
     Vector Search       Keyword Search
     (meaning)             (exact terms)
          ↓                   ↓
          └─────────┬─────────┘
                    ↓
              Combine scores
                    ↓
             Better candidates
```

This is a very important production RAG concept.

---

# 13. Vector Store vs Vector Database

These terms are often used interchangeably, so don't get too stuck on the terminology.

But conceptually:

### Vector Store

Main focus:

> Store embeddings and retrieve similar embeddings.

Could be relatively simple.

---

### Vector Database

Usually provides more complete database features such as:

- persistent storage
- vector indexes
- metadata filtering
- scaling
- replication
- CRUD operations
- namespaces / collections
- access controls
- hybrid search

So:

> Every vector database provides vector storage, but "vector store" can be used more broadly for simpler systems too.

In everyday RAG conversations, people often casually use both terms for the same thing.

---

# 14. Do you always need a dedicated vector database?

No.

This is an important practical point.

Suppose you're building a small product and already use:

**PostgreSQL.**

Instead of introducing another service like Pinecone or Qdrant, you could use:

**PostgreSQL + pgvector**

Then one database contains:

```text
Users
Orders
Documents
Metadata
Embeddings
```

`pgvector` adds vector similarity search directly to PostgreSQL. [GitHub](https://github.com/pgvector/pgvector?utm_source=chatgpt.com)

For many small-to-medium RAG applications, this can simplify the architecture significantly.

A dedicated vector database becomes more attractive when vector search itself is a major part of the workload or when you need specialized scaling/search capabilities.

---

# 15. A real-world storage example

Imagine a company has 20,000 internal documents.

After indexing:

```text
20,000 documents
        ↓
250,000 chunks
        ↓
250,000 embeddings
```

Your vector database might contain:

```python
{
    "id": "chunk_87451",

    "text":
        "Employees receive 25 days of annual leave.",

    "embedding":
        [...],

    "metadata": {
        "document": "employee_policy_2026.pdf",
        "department": "HR",
        "page": 43,
        "year": 2026
    }
}
```

User asks:

> How much annual leave do employees get?

Runtime:

```text
Question
    ↓
Embedding
    ↓
Filter:
department = HR
year = 2026
    ↓
Vector search
    ↓
Top relevant chunks
    ↓
LLM
```

Now you have a complete RAG retrieval foundation.

---

# 16. One subtle but important distinction

There are actually **two meanings of "index"** happening in our discussion.

### RAG indexing pipeline

When we said:

> "Index the documents"

we meant:

```text
Load
→ Clean
→ Chunk
→ Embed
→ Store
```

That's the overall RAG preprocessing process.

---

### Database vector index

Inside the vector database, the word **index** can mean a specialized search structure such as:

```text
HNSW index
IVFFlat index
```

Its purpose is to make nearest-neighbor search fast.

So:

> **RAG indexing** and **vector database indexing** are related, but they are not exactly the same concept.

That's worth remembering.

---

# 17. Our complete RAG Indexing pipeline

Now we can finally complete it.

```text
RAW KNOWLEDGE
     ↓
1. LOAD
Extract information from PDFs,
websites, databases, etc.
     ↓
2. CLEAN
Remove unnecessary noise.
     ↓
3. CHUNK
Create meaningful searchable pieces.
     ↓
4. METADATA
Preserve source, section, page,
permissions, category, etc.
     ↓
5. EMBED
Text → numerical vector.
     ↓
6. STORE
Store:
vector + text + metadata
     ↓
VECTOR / SEARCH INDEX
```

And that's the **indexing side of basic RAG complete**.

---

# What you should remember about vector stores

Keep these points in your revision notes:

**1. Vector stores keep embeddings, original chunks, and metadata.**

**2. Vector search finds embeddings close to the query embedding.**

**3. `Top-K` controls how many closest results we retrieve.**

**4. Similarity thresholds help reject irrelevant "closest" results.**

**5. Exact search compares broadly; ANN trades some recall for much better speed.**

**6. HNSW is one of the most common ANN indexing approaches.**

**7. Metadata filtering is critical for relevance and access control.**

**8. Hybrid search combines semantic vector search with exact keyword search.**

**9. You don't always need a separate vector DB—Postgres + pgvector may be enough.**

---

## Where we are in RAG now

We've finished:

**RAG Basics**

→ **Indexing**
- Loading
- Cleaning
- Chunking
- Metadata
- Embeddings
- Vector storage/index

So our next major chapter is:

# **Retrieval**

That is where we'll learn what happens **after the user asks a question**:

**Query → retrieval → Top-K candidates → filtering → hybrid search → reranking → context preparation → LLM**

### Sources for further reading

The Weaviate vector-search guide is useful for understanding query vectors, similarity/distance, thresholds, filters, and nearest-neighbor retrieval. [Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/vector-search?utm_source=chatgpt.com)  
[Weaviate — Vector Search](https://docs.weaviate.io/weaviate/concepts/search/vector-search?utm_source=chatgpt.com)

Their hybrid-search documentation clearly explains combining semantic vector retrieval with BM25 keyword search. [Weaviate Documentation](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search?utm_source=chatgpt.com)  
[Weaviate — Hybrid Search](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search?utm_source=chatgpt.com)

For seeing how vectors can live inside a traditional relational database, the official `pgvector` repository documents exact search, HNSW, IVFFlat, and filtering. [GitHub](https://github.com/pgvector/pgvector?utm_source=chatgpt.com)  
[pgvector documentation](https://github.com/pgvector/pgvector?utm_source=chatgpt.com)