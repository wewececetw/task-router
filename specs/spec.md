# Task Router Spec

## Overview
A task routing system that classifies incoming tasks by complexity and routes them to either a local model (via oMLX) or Claude API, optimizing for cost and speed.

## User Journey
1. User sends a task (via CLI or API)
2. System classifies task complexity (simple vs complex)
3. Simple tasks → local model (oMLX, e.g. Qwen2.5-14B)
4. Complex tasks → Claude API (via OAuth token or API key)
5. Result returned to user with metadata (which model, latency, etc.)

## Task Classification Rules
### Simple Tasks (→ Local Model)
- Code formatting / linting
- Simple translation (short text)
- Boilerplate generation
- Variable renaming
- Simple Q&A / factual lookup
- Text summarization (< 500 words)
- Regex generation
- JSON/YAML conversion

### Complex Tasks (→ Claude API)
- Architecture design
- Complex debugging
- Multi-step reasoning
- Code review with context
- Security analysis
- Performance optimization suggestions
- Large codebase refactoring plans

## Classification Method
1. **Rule-based** (primary): keyword matching + heuristics (length, presence of code, question complexity)
2. **Optional LLM classifier**: use local model to classify ambiguous tasks

## API Design
- OpenAI-compatible `/v1/chat/completions` endpoint
- Transparent routing — response includes `x-routed-to` header
- Configurable thresholds and routing rules
