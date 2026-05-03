# Answer Generation Skill — RAG-Based Response

## Description
This skill enables the Tutor Agent to generate high-quality educational answers
by combining retrieved context, conversation history, and LLM capabilities.

## RAG Pipeline
1. Context: Retrieved document chunks from Qdrant
2. History: Last 6 conversation turns from Memory Service
3. Question: Current student question
4. LLM: Ollama with Qwen 2.5 model

## Why RAG?
RAG (Retrieval-Augmented Generation) grounds LLM responses in actual study materials:
- Reduces hallucination
- Provides source-based answers
- Personalizes responses to student's own materials

## Prompt Structure

CONTEXT FROM STUDY MATERIALS:
[retrieved chunks]

CONVERSATION HISTORY:
[last 6 turns]

STUDENT QUESTION:
[current question]

ANSWER:
[LLM generates here]

## Model Selection
Qwen 2.5 was chosen because:
- Strong academic reasoning capabilities
- Open-source and runs locally via Ollama
- Good performance on educational Q&A tasks
- No external API costs, full data privacy

## Alternatives Considered

### GPT-4 (OpenAI)
- Better performance
- Expensive API costs
- Data sent to external servers, privacy concern
- Not open-source

### Llama 3.1
- Good open-source option
- Slightly weaker on academic tasks than Qwen 2.5
- Larger model size for same performance

### Mistral 7B
- Fast and lightweight
- Weaker reasoning for complex academic questions
- Good for simple Q&A but not deep explanations