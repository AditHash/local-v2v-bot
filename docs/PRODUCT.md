# Product requirements — local voice-to-voice bot

## Problem

Create a practical voice assistant POC that the developer can run on a Windows machine **without an NVIDIA GPU**. The user speaks; the assistant understands and replies aloud. The system should remain private, locally hosted, and inexpensive to iterate on.

## Primary success path — V1

1. Open the local web UI and grant microphone permission.
2. Record an English utterance, stop recording, and submit.
3. View the recognized speech text.
4. Receive a short, conversational LLM answer using previous context from this browser session.
5. Hear the synthesized reply and view separate STT, LLM, TTS and total times.
6. Clear the conversation and start a new one.

## Functional requirements

| ID | Requirement | V1 status |
| --- | --- | --- |
| F-01 | Capture microphone audio in a local web app | Scaffolded |
| F-02 | Transcribe recorded English speech locally on CPU | Scaffolded |
| F-03 | Send transcript and bounded session history to local Ollama | Scaffolded |
| F-04 | Synthesize and return spoken audio locally | Scaffolded |
| F-05 | Show transcripts, responses, history and stage timing | Scaffolded |
| F-06 | Clear conversation history on request | Scaffolded |
| F-07 | Helpful errors for silent input, missing model, unavailable Ollama | Partial |
| F-08 | Run offline after first-time installation/model downloads | Designed; unverified |
| F-09 | Continuous listening with streaming audio | Future |
| F-10 | Interrupt assistant speech (barge-in) | Future |
| F-11 | Native speech-to-speech via vLLM-Omni | Optional future |

**Scaffolded is not verified:** the V1 source code exists, but real hardware checks are pending.

## Nonfunctional requirements

- Default inference path must not require an external API, billing account, or GPU.
- Aim for an 8 GB RAM class Windows laptop; actual feasibility/latency must be measured on the real hardware. Do not promise a particular response time before benchmarking.
- Allow internet only for initial install and weight download; keep localhost bindings by default.
- Do not store session recordings/transcripts in a database. Minimize retention of synthesized temporary files. Clearly document local file handling.
- Keep error messages helpful without revealing secrets or stack traces to end users in a future production deployment.
- English-only in V1; multilingual support is an optional subsequent milestone.

## Non-goals for V1

Always-on listening, reliable full duplex, telephony integration, voice cloning, multimodal video, user accounts, cloud hosting, RAG, distributed scaling, and production-grade abuse/security controls.

## UX and acceptance examples

- User says "What is Python?" → sees transcription, hears a concise spoken explanation, and receives timing data.
- User follows with "Can you explain it in simpler terms?" → answer uses previous conversation.
- User records silence → gets a usable retry message, not a crash.
- User clicks Clear → the next query has no earlier conversation history.
- User disconnects internet **after** all weights are cached → local model processing continues (must be tested and documented).

## Product boundaries

Separate *native model capability* from *application behavior*: vLLM-Omni may support audio input/output on certain models and GPUs, but that does not make the current CPU app full-duplex. A modular STT → LLM → TTS chain is a valid end product if it provides a better measured experience.
