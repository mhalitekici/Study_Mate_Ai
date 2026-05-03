# Search Skill — Semantic Document Retrieval

## Description
This skill enables the Retrieval Agent to perform semantic search over uploaded study materials stored in Qdrant vector database.

## How It Works
1. User question is converted to a vector embedding using `nomic-embed-text` model via Ollama
2. The embedding is used to query Qdrant with a cosine similarity search
3. Results are filtered by `user_id` to ensure data isolation
4. Top-K most relevant document chunks are returned as context

## Technical Details
- **Vector Database**: Qdrant
- **Embedding Model**: nomic-embed-text (via Ollama)
- **Vector Size**: 768 dimensions
- **Distance Metric**: Cosine Similarity
- **Default Top-K**: 5 chunks

## Why Semantic Search?
Unlike keyword search, semantic search understands the meaning behind queries.
For example, searching for "photosynthesis process" will also retrieve
chunks about "how plants convert sunlight to energy" even without exact keyword matches.

## Isolation
Each search is filtered by `user_id`, ensuring students only retrieve
context from their own uploaded materials.