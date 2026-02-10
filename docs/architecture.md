```md
# System Architecture

## High-Level Overview

The AI Agent Orchestrator is designed as a multi-step AI pipeline rather than a single LLM call.
User requests are routed through specialized agents, each responsible for a specific task,
before producing a final validated response.

High-level flow:

User → Orchestrator → Intent Agent → Retrieval Agent → Tool Agent → Safety Agent → Final Response

---

## Components

### 1. Orchestrator

The Orchestrator is the central controller responsible for:
- Receiving user input
- Maintaining workflow state
- Deciding which agent to call next
- Enforcing hop limits to prevent infinite loops
- Recording workflow runs for observability

---

### 2. Intent Agent

Purpose:
- Understand what the user wants
- Classify the request (e.g., question, command, retrieval needed, tool needed)

Output:
- Structured intent classification used by the Orchestrator

---

### 3. Retrieval Agent (RAG)

Purpose:
- Retrieve relevant information from ingested documents
- Perform semantic search using embeddings
- Provide context to the LLM when answering document-based questions

Data source:
- PDF files uploaded via `/files/upload`
- Chunked and embedded into vector storage

---

### 4. Tool Agent

Purpose:
- Execute actions (if tools are available)
- Can be extended to integrate with external APIs, databases, or automation workflows

---

### 5. Safety / Policy Agent

Purpose:
- Validate the final response
- Enforce content policies
- Ensure output conforms to expected format

---

### 6. Final Response Builder

Purpose:
- Aggregate outputs from previous agents
- Build the final structured response returned to the user

---

## Storage Layer

The system supports pluggable storage backends:

### MongoDB Store
- Used in production environments
- Stores:
  - Uploaded documents
  - Embeddings
  - Workflow runs

### Local JSON Store
- Used as a fallback or during development
- Stores workflow runs and metadata locally

---

## LLM Backend (Ollama)

The system uses Ollama for local LLM inference:
- No paid API required
- Configurable model via environment variables
- Supports tool calling and structured outputs

---

## Observability

Workflow runs are recorded and can be inspected via:

- `GET /runs`
- `GET /runs/{run_id}`

Each run includes:
- Agent call sequence
- Intermediate outputs
- Final response

This enables debugging, evaluation, and grading transparency.