# Memory Management System

## Overview
StudyMate AI uses a hybrid memory management approach combining
short-term conversation context and long-term persistent storage.

## Memory Architecture

### Short-Term Memory (Conversation Context)
- **Storage**: MongoDB via Memory Service
- **Scope**: Last 6 conversation turns
- **Purpose**: Maintain conversation continuity within a session
- **Format**: List of {role, content} message pairs

### Long-Term Memory (Persistent History)
- **Storage**: MongoDB (conversations collection)
- **Scope**: All past interactions per user
- **Purpose**: Allow users to review learning history
- **Retrieval**: Chronological, paginated

## Why MongoDB?
MongoDB was chosen for memory storage because:
- **Flexible schema**: Conversation data has variable structure
- **Document model**: Natural fit for message objects
- **Async support**: Motor driver enables non-blocking operations
- **Scalability**: Horizontal scaling with sharding

## Alternatives Considered

### Redis
- ✅ Very fast
- ❌ Not persistent by default
- ❌ Limited query capabilities
- ❌ Not suitable for complex conversation history

### PostgreSQL
- ✅ ACID compliant
- ❌ Rigid schema for variable conversation data
- ❌ Less natural for document-style storage

### Vector Memory (RAG-based)
- ✅ Semantic retrieval of past conversations
- ❌ More complex to implement
- ❌ Overkill for conversation history at this scale
- 🔮 **Future improvement**: Upgrade to vector-based memory for smarter context retrieval

## Limitations & Future Improvements
1. **Current**: Simple chronological retrieval (last N messages)
2. **Improvement**: Semantic memory search using embeddings
3. **Improvement**: Memory summarization for long conversations
4. **Improvement**: User-controlled memory management (forget specific topics)