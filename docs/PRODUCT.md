# Product requirements — native speech-to-speech with vLLM-Omni

## Primary hypothesis

Can **vLLM-Omni** serve a speech-capable open-weight model that directly accepts human speech and generates meaningful spoken replies, enabling an eventual voice-to-voice chatbot **without orchestrating distinct STT, text-LLM and TTS models**?

This is an **evaluation POC**, not an immediate production chatbot.

## Users and environment

A developer builds the client from a Windows laptop **without a usable GPU**. A suitable self-managed Linux GPU host is required to test actual inference. A rented GPU may be used for a temporary test; it avoids paid model APIs but is not physically local/offline on the laptop.

## Proof requirements

| ID | Requirement | Current status |
| --- | --- | --- |
| P-01 | Start a compatible native duplex vLLM-Omni deployment | Not tested |
| P-02 | Connect over WebSocket and verify session capabilities | Not implemented |
| P-03 | Submit a recorded speech question as 16 kHz mono PCM16 WAV | Not implemented |
| P-04 | Receive playable generated audio directly from Omni model | Not implemented |
| P-05 | Test multiple conversational turns | Not implemented |
| P-06 | Measure first-audio, response, memory and GPU utilization | Not measured |
| P-07 | Capture live microphone audio and play streaming speech | Later milestone |
| P-08 | Support interrupts if capability flags permit | Later milestone |
| P-09 | Compare alternative Omni models on appropriate GPU | Optional |

## Definition of success

**Minimum pass:** a real, GPU-hosted vLLM-Omni duplex model processes at least one English voice utterance and generates an audible, relevant spoken reply. A mock WebSocket test **does not** meet this criterion.

**Extended pass:** multi-turn voice conversation with measured latency and documented handling of overlapping speech/interruptions, if the model supports them.

**Non-goals:** telephony/phone numbers, cloud speech APIs, RAG, user authentication, large-scale concurrency, production SLAs, voice cloning and automated STT/TTS chains.

## Baseline code disclaimer

The repository initially contains `app.py`, a separate Whisper → Ollama → Piper Gradio implementation. Treat it as a fallback comparator ONLY. Running it is not proof of native vLLM-Omni audio ability.
