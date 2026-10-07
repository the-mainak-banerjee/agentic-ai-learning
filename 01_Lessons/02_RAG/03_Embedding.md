# Embeddings 

## 1. What is an Embedding?

An **embedding** is a list of numbers that represents the meaning of some data.

In RAG, the data is usually text.

Example:

```text
"The cat is sleeping on the sofa."
        ↓
Embedding model
        ↓
[0.18, -0.42, 0.73, 0.09, ...]
```

That list of numbers is called a **vector**.

The most important idea:

> Texts with similar meanings tend to get vectors that are close to each other.

---

## 2. Why Do We Need Embeddings?

Embeddings help us search by **meaning**, not only by exact keywords.

Example:

Stored text:

```text
Employees can work from home three days per week.
```

User asks:

```text
Can employees work remotely?
```

The wording is different, but the meaning is very similar.

Embedding-based retrieval can recognize that similarity.

This is called **semantic search**.

---

## 3. Think of Embeddings as Coordinates

A useful mental model is a map.

On a normal map, places have coordinates.

With embeddings, pieces of text get coordinates in a **semantic space**.

Conceptually:

```text
Animals

cat      ●
kitten   ●
dog      ●


Vehicles

car          ●
automobile   ●
truck        ●
```

Similar concepts appear closer together.

In reality, embeddings usually have hundreds or thousands of dimensions, not just two.

---

## 4. What Does Dimension Mean?

Example:

```text
[0.8, 0.1, 0.6]
```

This vector has **3 dimensions** because it contains three numbers.

Real embedding models produce much larger vectors.

Important:

> Individual dimensions usually do not map cleanly to simple ideas such as “animals”, “vehicles”, or “emotion”.

Meaning is distributed across many dimensions.

---

## 5. How Are Embeddings Learned?

Embedding models learn patterns during training.

They learn that words and phrases such as:

```text
car
automobile
vehicle
```

are related.

They also learn relationships such as:

```text
forgot password
password reset
recover account access
```

You do not manually define these relationships.

The model learns them from training data.

---

## 6. Embeddings in the RAG Indexing Pipeline

Our indexing pipeline is:

```text
Document
  ↓
Load
  ↓
Clean
  ↓
Chunk
  ↓
Embedding Model
  ↓
Vector for each chunk
  ↓
Store
```

Example chunks:

```text
Chunk 1:
Employees receive 20 paid vacation days.

Chunk 2:
Employees may work remotely three days per week.

Chunk 3:
Health insurance begins after 30 days.
```

Each chunk gets its own embedding.

Example:

```python
chunk_1_embedding = [0.12, 0.53, -0.21, ...]
chunk_2_embedding = [0.71, -0.13, 0.46, ...]
chunk_3_embedding = [-0.31, 0.22, 0.67, ...]
```

Usually we store:

```text
original text + embedding + metadata
```

Example:

```python
{
    "text": "Employees may work remotely three days per week.",
    "embedding": [0.71, -0.13, 0.46, ...],
    "metadata": {
        "source": "employee_handbook.pdf"
    }
}
```

---

## 7. What Happens During Retrieval?

User asks:

```text
How often can I work from home?
```

We embed the question too.

```text
User question
    ↓
Embedding model
    ↓
Query vector
```

Then the system compares the query vector with stored chunk vectors.

The most semantically similar chunks are retrieved.

Example:

```text
Question
+
Retrieved chunk
    ↓
LLM
    ↓
Final answer
```

So embeddings connect **indexing** and **retrieval**.

---

## 8. How Do We Measure Which Vectors Are Close?

Common similarity or distance methods include:

- cosine similarity
- dot product
- Euclidean distance

The easiest one to understand conceptually is **cosine similarity**.

Think of vectors like arrows.

If two arrows point in almost the same direction:

```text
↗
↗
```

they are highly similar.

If they point in very different directions:

```text
↗
←
```

they are less similar.

The similarity function helps the retriever decide which stored vectors are closest to the query vector.

---

## 9. Real-Life Example

Imagine an airline assistant.

Knowledge base:

```text
Chunk A:
Passengers may bring one cabin bag weighing up to 7 kg.

Chunk B:
Checked baggage allowance is 20 kg.

Chunk C:
Flight cancellation refunds are processed within seven business days.
```

User asks:

```text
How heavy can my carry-on be?
```

The exact phrase **carry-on** is different from **cabin bag**.

But the meanings are similar.

Embedding search can still retrieve Chunk A.

---

## 10. Embeddings vs Keyword Search

Example:

Document:

```text
The customer may terminate the subscription at any time.
```

Query:

```text
Can I cancel my plan whenever I want?
```

Different words:

```text
terminate ↔ cancel
subscription ↔ plan
at any time ↔ whenever I want
```

The meaning is still similar.

This is one of the biggest advantages of embedding-based semantic search.

---

## 11. Embeddings Are Not Perfect

Embeddings can struggle with very exact information such as:

- numbers
- IDs
- dates
- product codes
- exact phrases
- rare technical terms
- proper names

Example:

```text
The policy became effective in 2023.
The policy became effective in 2024.
```

These two sentences are semantically almost identical.

Only the year is different.

This is one reason production RAG systems often combine:

```text
semantic search + keyword search
```

This is called **hybrid search**.

---

## 12. Embeddings Compress Meaning

An embedding is a compressed semantic representation.

Example:

```text
500-token text chunk
        ↓
Embedding model
        ↓
Vector
```

The vector helps the system **find** the chunk.

But the vector is not a readable replacement for the original text.

So:

```text
Embedding
```

cannot normally be used to perfectly reconstruct the original chunk.

This is why we keep:

```text
vector + original text
```

The vector finds the information.

The original text gives the LLM the actual information.

---

## 13. Embedding Model vs LLM

These are different tools with different jobs.

### Embedding model

Input:

```text
How do I reset my password?
```

Output:

```text
[0.14, -0.28, 0.71, ...]
```

Job:

> Represent meaning numerically.

### LLM

Input:

```text
Question + context
```

Output:

```text
Click Forgot Password and follow the reset link.
```

Job:

> Generate language.

In RAG:

```text
Embedding model
    ↓
helps retrieve information

LLM
    ↓
uses retrieved information to generate an answer
```

---

## 14. Use Compatible Embeddings

During indexing, document chunks are embedded.

During retrieval, the user query is embedded.

These embeddings must belong to the same compatible vector space.

Normally this means using the same embedding model and compatible configuration for both.

Conceptually:

```text
Documents → Model A
Queries   → Model A
```

If you embed documents with Model A but queries with an incompatible Model B, vector comparisons may become meaningless.

---

## 15. What Happens If You Change Embedding Models?

Suppose you indexed one million chunks using one embedding model.

Later, you switch to a different embedding model.

Usually you need to:

```text
re-embed the stored chunks
```

and often rebuild the index.

Why?

Because the new model creates a different embedding space.

This is an important production consideration.

---

## 16. Embeddings Beyond RAG

Embeddings are useful for many AI engineering tasks:

- semantic search
- RAG
- recommendation systems
- clustering
- duplicate detection
- classification
- anomaly detection
- similarity matching

Example:

```text
Customer ticket:
"I was charged twice."

Similar tickets:
"Duplicate payment"
"Double billing"
"Charged two times"
```

Embeddings can group these together even though the wording differs.

---

## 17. Connection Between Chunking and Embeddings

Chunking quality directly affects embedding quality.

Bad chunk:

```text
Password reset
+
vacation policy
+
pricing
+
refund policy
```

One vector now has to represent several unrelated topics.

Better:

```text
Chunk 1 → Password reset
Chunk 2 → Vacation policy
Chunk 3 → Pricing
Chunk 4 → Refund policy
```

Each embedding now represents a much clearer concept.

So:

> **Chunking quality affects embedding quality, which affects retrieval quality.**

---

## 18. Complete Mental Model

### During Indexing

```text
Text chunk
   ↓
Embedding model
   ↓
Vector
   ↓
Store vector + text + metadata
```

### During Retrieval

```text
User question
   ↓
Embedding model
   ↓
Query vector
   ↓
Compare with stored vectors
   ↓
Retrieve most similar chunks
   ↓
Give chunks to LLM
```

---

# Quick Revision

Remember these five points:

1. **Embedding = numerical representation of meaning**
2. **Similar meaning → vectors tend to be closer**
3. **Embeddings enable semantic search**
4. **Both document chunks and user queries are embedded**
5. **The vector finds the information; the original text gives the LLM the information**

---

## RAG Indexing So Far

```text
Load
→ Clean
→ Chunk
→ Embed
→ Store
```

---

## One-Sentence Mental Model

> **Embeddings convert text into numerical vectors so a RAG system can compare meanings and retrieve the most relevant chunks.**



