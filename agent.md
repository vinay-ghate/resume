# 🤖 AI Agent Guide: Resume Keyword Extraction & Metadata Synchronization

This document is the operational guide for AI agents (and human contributors) working in this repository. Whenever a LaTeX resume source file (`.tex`) is created, modified, renamed, or removed, the agent must ensure that [`metadata.json`](./metadata.json) in the repository root is synchronized.

---

## 📌 Repository Overview

LaTeX resumes are archived across tracks and variants, compiled via GitHub Actions, and served on GitHub Pages.

- **Tracks (folders)**: e.g. `Dev/`, `GenAI/`, or future folders like `Research/`, `Cloud/`.
- **Variants (files)**: numbered `.tex` files inside each track (e.g. `1001.tex`, `2001.tex`).
- **Metadata index (`metadata.json`)**: root-level index of all technical keywords extracted per resume file.

### Scan scope
- Scan only `*.tex` files located **directly inside top-level track folders**.
- Ignore: `.git/`, `.github/`, `scripts/`, build or output directories (e.g. `dist/`, `build/`, `public/`), and any non-`.tex` file.
- A new top-level folder containing `.tex` files is a new track and must be added to `metadata.json`.

---

## 🗂️ Metadata Schema

`metadata.json` is a two-level nested dictionary:

```json
{
  "<Folder_Name>": {
    "<Filename.tex>": [
      "Keyword 1",
      "Keyword 2",
      "Keyword 3"
    ]
  }
}
```

### Schema rules
1. **Top-level keys**: exact directory name relative to the repo root (e.g. `"Dev"`, `"GenAI"`).
2. **Second-level keys**: exact filename including extension (e.g. `"2001.tex"`).
3. **Keyword list**: a JSON array of strings (`string[]`) that is:
   - **Deduplicated**: no duplicate terms within the same file.
   - **Sorted** alphabetically, case-insensitive (Python: `sorted(set(keywords), key=str.lower)`), for deterministic Git diffs.
   - **Canonically cased**: standard industry casing (`PostgreSQL`, `FastAPI`, `mTLS`, `Kubernetes`).
   - **Grounded**: only skills, tools, frameworks, concepts, and certifications **explicitly mentioned** in that document. Never infer or add related terms.
4. **Ordering of keys**: folders and filenames sorted alphabetically.
5. **Formatting**: 2-space indentation, UTF-8, trailing newline.

---

## 🔍 Keyword Extraction Taxonomy

Extract terms from the categories below. The examples are illustrative only; **extract a term only if it appears in the file**.

| Category | Example Terms |
| :--- | :--- |
| **Languages & Scripting** | `Python`, `SQL`, `Java`, `Bash`, `TypeScript`, `CSS`, `YAML` |
| **Backend & Microservices** | `FastAPI`, `Django`, `Flask`, `SQLAlchemy`, `asyncio`, `REST APIs`, `GraphQL`, `gRPC`, `Protocol Buffers`, `Microservices` |
| **Architecture & Systems** | `Event-Driven Architecture`, `Distributed Systems`, `Scalability`, `Caching`, `Load Balancing`, `Message Queues`, `HLD & LLD`, `OOP` |
| **Messaging & Streaming** | `Apache Kafka`, `Strimzi Kafka`, `Kafka Partitioning`, `Kafka Producers & Consumers`, `WebSockets` |
| **Databases & Stores** | `PostgreSQL`, `MySQL`, `MongoDB`, `ChromaDB`, `Oracle DB`, `Hadoop`, `Vector Databases`, `Schema Design` |
| **Cloud & DevOps** | `Kubernetes`, `Docker`, `Docker Compose`, `Helm`, `Linux`, `SSH`, `CI/CD`, `GitHub Actions`, `Prometheus`, `Grafana` |
| **AI, LLM & Agentic AI** | `LangGraph`, `CrewAI`, `AutoGen`, `LangChain`, `LlamaIndex`, `MCP (Model Context Protocol)`, `Tool Calling`, `Agent Memory`, `ReAct Framework`, `Plan-and-Execute` |
| **RAG & GenAI Concepts** | `Retrieval-Augmented Generation (RAG)`, `Modular RAG`, `Vector Embeddings`, `Semantic Search`, `Fine-Tuning`, `PEFT`, `LoRA`, `QLoRA`, `RLHF`, `NL2SQL` |
| **LLMs & Models** | `OpenAI API`, `Gemini API`, `Hugging Face`, `NVIDIA NIM`, `Llama 3.1 8B`, `Small Language Models (SLMs)`, `Multi-Modal LLMs` |
| **LLMOps & Governance** | `Responsible AI`, `Prompt Injection Defenses`, `Anti-Hallucination Guardrails`, `LLM Evaluation`, `Pyrit`, `Microsoft HAX Toolkit`, `BLEU Score` |
| **Security & Networking** | `mTLS`, `TCP/IP`, `HTTP/HTTPS`, `Cyber Security`, `Data Isolation`, `Data Governance`, `Access Control` |
| **Certifications** | `Confluent Data Streaming Engineer`, `Microsoft Certified: Azure AI Fundamentals`, `AWS Certified AI Practitioner`, `OCI 2025 Generative AI Professional` |

### Normalization rules
- **Form**: if a term appears both abbreviated and expanded (e.g. `RAG` and `Retrieval-Augmented Generation (RAG)`), keep **one** entry, using the canonical form from the table above. If a term is not in the table, use the form as written in the resume.
- **Variants**: merge trivial variants (`Postgres` → `PostgreSQL`, `K8s` → `Kubernetes`, `Github Actions` → `GitHub Actions`, `Rest API` → `REST APIs`).
- **Granularity**: prefer atomic terms. Do not extract full sentences, metrics, or achievements (e.g. skip "reduced latency by 40%").

### 🔒 Privacy: what NOT to extract
`metadata.json` is publicly served via GitHub Pages. Do **not** extract:
- Employer, client, or institution names.
- Project, product, or internal system names that identify an employer or client.
- Personal details (name, email, phone, location, links).
Only generic technologies, concepts, and public certifications belong in the index.

---

## 🧹 LaTeX Parsing Rules

1. **Remove comments**: strip text after an unescaped `%` to end of line. (`\%` is a literal percent, not a comment.)
2. **Strip formatting commands**, keeping their content: `\textbf{...}`, `\textit{...}`, `\emph{...}`, `\small{...}`, `\underline{...}`, `\scshape`, `\fontsize{...}{...}`, and custom macros such as `\dv{...}`.
3. **Links**: `\href{url}{text}` → keep `text`, discard `url`. Handle nested braces.
4. **Structural commands**: drop `\item`, `\\`, `\,`, `\;`, `\hfill`, `\vspace{...}`, `\hspace{...}`, `\begin{...}`/`\end{...}`, and similar layout tokens.
5. **Unescape special characters**: `\&` → `&`, `\%` → `%`, `\$` → `$`, `\#` → `#`, `\_` → `_`, `~` → space.
6. **Split lists**: skills lines like `Languages: Python, SQL, Bash` → split on commas and semicolons after removing the category label.
7. **Focus sections** (in priority order):
   1. `\section{Technical Skills}` (primary source)
   2. `\section{Summary}`
   3. `\section{Experience}`
   4. `\section{Projects}`
   5. `\section{Certifications}`
   Section names may vary slightly (e.g. `Skills`, `Professional Experience`); match by intent.

---

## ⚡ Execution Protocol for AI Agents

Trigger: any add, modify, rename, or delete of a `.tex` file in a track folder.

### Protocol A: Script execution (preferred, if the script exists)
Run from the repository root:
```bash
python scripts/update_metadata.py            # update metadata.json
python scripts/update_metadata.py --validate # check only, no writes (non-zero exit on drift)
```
If `scripts/update_metadata.py` does not exist, use Protocol B.

### Protocol B: Direct LLM extraction and editing
1. Read the added or updated `.tex` file.
2. Extract keywords following the Taxonomy, Normalization, Privacy, and Parsing rules.
3. Read the existing `metadata.json` (create `{}` if missing).
4. Set `metadata[folder][filename] = sorted(set(keywords), key=str.lower)`.
5. For renamed files, move the entry to the new key. For deleted files, remove the entry, and remove the folder key if it becomes empty.
6. Sort folder keys and filename keys alphabetically.
7. Write back with 2-space indentation and a trailing newline.
8. Verify the JSON parses.

---

## 📋 Checklist Before Completing a Task

- [ ] Every `.tex` file in every track folder is indexed.
- [ ] No phantom entries remain for deleted or renamed files; no empty folder keys.
- [ ] Keywords are deduplicated, case-insensitively sorted, and canonically cased.
- [ ] Every keyword is explicitly present in its source file.
- [ ] No employer, client, project, or personal identifiers were extracted.
- [ ] `metadata.json` is valid JSON with 2-space indentation.
- [ ] `python scripts/update_metadata.py --validate` passes (if the script exists).