## Our single problem

Let's imagine you're building an AI feature for **QuizMB**.

> **User uploads a PDF containing a technical article and asks:**
>
> "Create 5 high-quality multiple-choice questions from this document. Each question should have 4 options, exactly one correct answer, an explanation, and a difficulty level."

This is realistic because it involves:

* LLM reasoning
* structured output
* document context
* validation
* multiple model calls
* tools
* potentially multimodal input
* reliability

We'll use this same problem for all 13 techniques.

---

# First: the mental map

Before diving in, understand what each technique is trying to solve:

| Technique                       | Main problem it solves                                |
| ------------------------------- | ----------------------------------------------------- |
| **Zero-shot**                   | "Just do the task."                                   |
| **Few-shot**                    | "Here's what good output looks like."                 |
| **CoT**                         | "Reason through the task."                            |
| **Meta-prompting**              | "Design/improve the prompt or process itself."        |
| **Self-consistency**            | "Don't trust one reasoning attempt."                  |
| **General knowledge prompting** | "Give the model useful domain knowledge/context."     |
| **Prompt chaining**             | "Break a complicated task into stages."               |
| **Tree of Thoughts**            | "Explore multiple possible solutions."                |
| **Directional Stimulus**        | "Give the model hints/directions without solving it." |
| **ReAct**                       | "Reason + use tools + observe results."               |
| **Reflexion**                   | "Try → evaluate → learn from mistakes → retry."       |
| **Graph prompting**             | "Represent relationships explicitly."                 |
| **Multimodal CoT**              | "Reason using text + images/other modalities."        |

Now let's build them one by one.

---

# 1. Zero-shot prompting

You give the model **the task without examples**.

### Prompt

```text
Create 5 multiple-choice questions from the following document.

Requirements:
- 4 options per question
- Exactly one correct answer
- Include an explanation
- Include difficulty: easy, medium, or hard

Document:
{{document}}
```

That's it.

There are **zero examples**.

### Developer implementation

```ts
const response = await llm.generate({
  prompt: `
    Create 5 multiple-choice questions from this document.

    Requirements:
    - 4 options
    - Exactly one correct answer
    - Include explanation
    - Include difficulty

    Document:
    ${document}
  `
});
```

### When useful

Good when:

* task is straightforward
* output format is obvious
* you don't need extremely consistent results

### Weakness

The model doesn't really know **what you consider a "good question."**

That's where few-shot comes in.

---

# 2. Few-shot prompting

Instead of only describing the task, you give the model **examples of desired behavior**.

### Prompt

```text
You create high-quality technical quiz questions.

Here are examples.

Example 1:

Input:
"React Server Components allow components to execute on the server..."

Output:
{
  "question": "Where does a React Server Component primarily execute?",
  "options": [
    "Browser",
    "Server",
    "Database",
    "CDN"
  ],
  "answer": "Server",
  "explanation": "React Server Components execute on the server...",
  "difficulty": "easy"
}

Example 2:

Input:
"An index allows databases to locate rows more efficiently..."

Output:
{
  "question": "What is the primary purpose of a database index?",
  "options": [
    "Store backups",
    "Improve query lookup performance",
    "Encrypt data",
    "Validate schemas"
  ],
  "answer": "Improve query lookup performance",
  "explanation": "...",
  "difficulty": "medium"
}

Now create 5 questions from:

{{document}}
```

The examples teach the model:

* question style
* option style
* explanation depth
* difficulty classification
* output structure

### Mental model

```text
Zero-shot:

Instructions → Output


Few-shot:

Instructions
     +
Examples
     ↓
Output
```

### Important AI-engineering lesson

**Few-shot examples are often more powerful than adding another paragraph of instructions.**

Instead of:

> "Make the questions high quality, technically accurate, interesting, not too obvious..."

sometimes just showing **3 excellent examples** works better.

---

# 3. Chain-of-Thought (CoT)

Now suppose creating a question requires reasoning.

For example:

> The document describes a system with caching, database queries and API calls. Create a question that tests whether the user understands which operation benefits most from caching.

We can ask the model to reason through the task.

Conceptually:

```text
Analyze the source
      ↓
Identify important concepts
      ↓
Find relationships
      ↓
Create candidate question
      ↓
Check answer
      ↓
Generate final output
```

A classic prompt might say:

```text
Analyze the document step by step before creating the questions.

For each question:
1. Identify an important concept.
2. Determine what understanding should be tested.
3. Construct plausible distractors.
4. Verify that exactly one answer is correct.
5. Assign difficulty.
6. Return the final question.
```

### Important modern nuance

As an AI engineer, **don't assume you need to force the model to expose its private chain-of-thought**.

You can ask for a concise rationale, intermediate artifact, or validation result instead:

```text
Before producing the final question, identify:
- concept being tested
- expected answer
- why the distractors are incorrect
```

That's often a better production pattern.

---

# 4. Meta-prompting

This one is different.

Instead of asking:

> "Create questions."

you ask the model to **design the process/prompt that should create the questions**.

For example:

```text
You are an expert prompt engineer.

Design the best prompt for generating technical
multiple-choice questions from a document.

The generated prompt must ensure:
- factual accuracy
- plausible distractors
- appropriate difficulty
- no duplicate questions
- exactly one correct answer
- structured JSON output

Return:
1. The final prompt
2. Why each instruction is included
```

The model produces something like:

```text
SYSTEM:
You are a technical assessment generator...

RULES:
...

OUTPUT SCHEMA:
...
```

Then **your application uses that generated prompt**.

### Architecture

```text
Your application
      ↓
Meta-prompt
      ↓
LLM designs prompt
      ↓
Generated prompt
      ↓
LLM generates quiz
      ↓
Questions
```

This is useful when you're building **dynamic AI systems** where prompts themselves need to adapt.

---

# 5. Self-consistency

Now imagine the model generates a question:

```text
Question:
Which caching strategy is appropriate here?

Answer: B
```

But maybe it made a reasoning mistake.

Instead of trusting one generation:

```text
Document
   ↓
LLM → B
```

you generate several independent solutions:

```text
              Document
                  │
       ┌──────────┼──────────┐
       ↓          ↓          ↓
      LLM        LLM        LLM
       ↓          ↓          ↓
       B          B          C
       │          │          │
       └──────────┼──────────┘
                  ↓
             Majority vote
                  ↓
                  B
```

In code:

```ts
const attempts = await Promise.all(
  Array.from({ length: 5 }, () =>
    llm.generate(prompt)
  )
);
```

Then:

```ts
const finalAnswer = majorityVote(attempts);
```

### For QuizMB

You could ask 5 generations:

> "Determine which option is correct and return only the answer."

Then use agreement as a confidence signal.

For example:

```text
B B B B C

Agreement = 4/5
```

You can decide:

```text
>= 80% → accept
< 80%  → send for validation
```

That's where self-consistency becomes an **engineering technique**, not just prompting.

---

# 6. General Knowledge Prompting

This is essentially about giving the model **relevant background knowledge/context** that it needs to perform the task correctly.

Suppose your PDF says:

> "The system uses eventual consistency."

But your quiz generator doesn't understand the concept well enough to construct good distractors.

You can provide domain context:

```text
You are generating questions for software engineers.

Relevant domain knowledge:

Eventual consistency means that after a write,
replicas may temporarily contain different values,
but assuming no further writes, replicas will
eventually converge.

Important distinction:
Eventual consistency does NOT guarantee immediate
read-after-write consistency.

Now use this knowledge together with the document
to generate the question.
```

### Why this matters

You're essentially doing:

```text
Document
   +
Domain knowledge
   +
Task instructions
        ↓
      LLM
```

This is related to the broader idea of **knowledge grounding**.

In production, you might retrieve this knowledge from:

* vector database
* documentation
* knowledge base
* database
* web search
* internal company docs

So this technique connects naturally to **RAG**.

---

# 7. Prompt Chaining

This is **extremely important for AI engineering**.

Don't make one gigantic prompt do everything.

Break the task into stages.

Instead of:

```text
PDF → generate perfect quiz
```

do:

```text
PDF
 ↓
Extract concepts
 ↓
Generate questions
 ↓
Generate distractors
 ↓
Validate questions
 ↓
Classify difficulty
 ↓
Final JSON
```

### Chain 1

```text
Extract important concepts from the document.

Return 10 concepts.
```

Output:

```json
[
  "Caching",
  "Database indexing",
  "Eventual consistency"
]
```

### Chain 2

```text
Using these concepts, generate 10 candidate questions.
```

### Chain 3

```text
Review these questions.

Check:
- factual correctness
- duplicate questions
- ambiguous wording
- multiple correct answers
```

### Chain 4

```text
Fix the questions that failed validation.
```

### Architecture

```text
             PDF
              ↓
       Concept Extraction
              ↓
       Question Generation
              ↓
          Validation
              ↓
        Error Correction
              ↓
       Difficulty Scoring
              ↓
          Final Quiz
```

This is how you start moving from **prompt engineering → AI engineering**.

You're designing an **LLM pipeline**.

---

# 8. Tree of Thoughts

Now imagine there are multiple ways to create a good question.

Instead of generating one:

```text
Concept
   ↓
Question
```

generate several candidate approaches:

```text
                  Concept
                     │
          ┌──────────┼──────────┐
          ↓          ↓          ↓
       Definition  Scenario   Comparison
          │          │          │
       Question   Question   Question
          │          │          │
          └──────────┼──────────┘
                     ↓
                  Evaluate
                     ↓
              Select candidate
```

Prompt:

```text
Generate three different approaches for testing
the following concept:

Concept:
Database indexing

Approach 1:
Test conceptual understanding.

Approach 2:
Test practical debugging.

Approach 3:
Test performance reasoning.

For each approach, create a candidate question.
Then evaluate each candidate for:
- clarity
- difficulty
- technical accuracy
- quality of distractors

Select the strongest candidate.
```

That's ToT.

### Difference from self-consistency

**Self-consistency:**

> "Give me several attempts and see which answer agrees."

**ToT:**

> "Explore different approaches and evaluate the paths."

---

# 9. Directional Stimulus Prompting

This is subtle but useful.

Instead of telling the model **the answer**, you give it a **directional hint**.

Suppose the correct question should test performance implications.

Don't say:

```text
The answer should be about database indexing.
```

Instead:

```text
Focus on:
- lookup efficiency
- data access patterns
- tradeoffs between reads and writes
```

Then:

```text
Create a question about database indexing.

Focus your reasoning on:
- lookup efficiency
- read/write tradeoffs
- when indexes become useful
```

You're **steering the model toward useful reasoning** without explicitly giving it the solution.

### Mental model

```text
Normal:

Problem → LLM → Answer


Directional stimulus:

Problem
   +
Useful direction/hint
   ↓
  LLM
   ↓
Answer
```

This is especially useful when you know **what dimension the model should pay attention to**.

---

# 10. ReAct

Now let's make QuizMB an actual **agent**.

Suppose the user asks:

> "Create questions about the most important concepts in this PDF and verify that the concepts are technically correct."

The AI might have tools:

```text
search_document()
get_document_section()
search_web()
validate_question()
save_question()
```

Now the model can operate:

```text
Thought
   ↓
Action → search_document()
   ↓
Observation
   ↓
Thought
   ↓
Action → get_document_section()
   ↓
Observation
   ↓
Thought
   ↓
Action → validate_question()
   ↓
Observation
   ↓
Final answer
```

For example:

```text
User:
Create a question about Redis persistence.

Agent:
I need to inspect the document.

→ search_document("Redis persistence")

Tool:
Found section 4.

Agent:
I need more context.

→ get_document_section(4)

Tool:
...

Agent:
I'll generate the question.

→ validate_question(question)

Tool:
Multiple correct answers detected.

Agent:
I'll revise it.

→ validate_question(revised_question)

Tool:
Valid.

Agent:
Return question.
```

That's **ReAct**.

And this is very close to how modern agentic systems are architected.

---

# 11. Reflexion

Reflexion adds **self-evaluation and learning from failure**.

The loop becomes:

```text
Generate
   ↓
Evaluate
   ↓
What went wrong?
   ↓
Improve
   ↓
Generate again
```

Suppose the model generates:

```text
Question:
Which two options are correct?

A...
B...
C...
D...
```

Your validator says:

```text
FAIL

Reason:
Both B and C are technically correct.
```

Instead of simply throwing it away:

```text
Validator
   ↓
Feedback:
"Two answers are correct."
   ↓
LLM
   ↓
Revised question
```

Prompt:

```text
Here is the generated question:

{{question}}

Validation result:
FAIL

Reason:
Two options are technically correct.

Reflect on the problem and identify what caused
the ambiguity.

Then produce a corrected version.
```

### Architecture

```text
              Generate
                 ↓
              Validate
                 ↓
          ┌──────┴──────┐
          ↓             ↓
        PASS           FAIL
          ↓             ↓
        Done         Reflect
                        ↓
                      Fix
                        ↓
                    Validate
```

### ReAct vs Reflexion

ReAct:

> **"What action should I take next?"**

Reflexion:

> **"What did I do wrong, and how should I improve?"**

They can absolutely be combined.

---

# 12. Graph Prompting

This becomes useful when the information is highly relational.

Imagine your PDF contains:

```text
React
  ↓
Server Components
  ↓
Server Rendering
  ↓
Caching
  ↓
Performance
```

Instead of giving the model a flat list:

```text
React
Server Components
Caching
Performance
```

you represent relationships:

```text
React
 └── Server Components
       └── Server Rendering
             └── Caching
                   └── Performance
```

Or:

```text
React → Server Components
Server Components → Server Rendering
Server Rendering → Caching
Caching → Performance
```

Then prompt:

```text
The following knowledge graph represents the
relationships in the document:

React → Server Components
Server Components → Server Rendering
Server Rendering → Caching
Caching → Performance

Generate a question that tests one of these
relationships rather than simply testing a definition.
```

Now the model can create:

> "How can caching affect the performance of an application using server-rendered components?"

### Why graph prompting matters

It helps when you're dealing with:

* knowledge graphs
* dependency relationships
* entity relationships
* multi-hop reasoning
* organizational structures
* recommendation systems

Think:

```text
Normal prompting:

A
B
C
D


Graph prompting:

A → B → C
     ↓
     D
```

The **relationships themselves become part of the prompt**.

---

# 13. Multimodal CoT

Now suppose your PDF contains:

* text
* diagrams
* architecture diagrams
* screenshots
* charts

A text-only model might miss important information.

Imagine this architecture diagram:

```text
Client
   ↓
API Gateway
   ↓
Load Balancer
   ↓
Server
   ↓
Redis
   ↓
PostgreSQL
```

Instead of extracting only text, you provide the **image + question** to a multimodal model.

Prompt:

```text
Analyze this architecture diagram.

Identify:
1. The major components.
2. The data flow.
3. The role of Redis.
4. A potential bottleneck.

Then create one multiple-choice question
that tests understanding of the architecture.
```

The model reasons using:

```text
Image
  +
Text
  +
Domain knowledge
      ↓
Multimodal reasoning
      ↓
Question
```

That's **Multimodal CoT**.

It becomes particularly useful for:

* diagrams
* charts
* screenshots
* UI analysis
* handwritten problems
* medical/scientific images
* architecture diagrams
* documents containing mixed media

---

# Now put everything together

This is the part I really want you to understand as an **AI engineer**.

These aren't necessarily competing techniques.

You can **combine them**.

For your QuizMB system, a sophisticated pipeline could look like:

```text
                         PDF
                          │
              ┌───────────┴───────────┐
              │                       │
            Text                    Images
              │                       │
              └───────────┬───────────┘
                          ↓
                  Multimodal Analysis
                          ↓
                   Extract Concepts
                          ↓
                 Knowledge Graph
                          ↓
              ┌───────────┴───────────┐
              ↓                       ↓
        General Knowledge       Document Context
              │                       │
              └───────────┬───────────┘
                          ↓
                    Prompt Chain
                          ↓
                Generate Candidates
                          ↓
                    Tree of Thoughts
                          ↓
                Multiple Candidates
                          ↓
                   Self-Consistency
                          ↓
                     Validation
                          ↓
                      Reflexion
                          ↓
                  ReAct Agent
                          ↓
                    Final Quiz
```

That's much closer to **real AI engineering** than memorizing prompt templates.

---

# The most important distinction

If you're serious about becoming an AI engineer, organize these 13 techniques into **four categories**.

### 1. Tell the model how to solve

```text
Zero-shot
Few-shot
CoT
Directional Stimulus
General Knowledge
```

These primarily modify **the prompt**.

---

### 2. Make reasoning more reliable

```text
Self-Consistency
Tree of Thoughts
Reflexion
```

These introduce **multiple attempts, evaluation, or search**.

---

### 3. Build an AI workflow

```text
Prompt Chaining
ReAct
Graph Prompting
```

These move beyond one prompt into **orchestration**.

---

### 4. Add other modalities

```text
Multimodal CoT
```

This expands reasoning beyond text.

---

# Your AI Engineer mental model

Don't memorize:

> "ToT is this prompt. ReAct is that prompt."

Instead, ask:

```text
                    AI Problem
                        │
          ┌─────────────┼─────────────┐
          ↓             ↓             ↓
     Need examples?  Need tools?   Need reliability?
          │             │             │
       Few-shot       ReAct      Self-consistency
                                      │
                                Need exploration?
                                      │
                                     ToT
                                      │
                                Need learning?
                                      │
                                  Reflexion
```

**That's the real skill.**

When you encounter a new AI problem, you should be able to look at it and think:

> "Is this a prompting problem, a reasoning problem, a context problem, a tool-use problem, or an orchestration problem?"

Then choose the appropriate technique.