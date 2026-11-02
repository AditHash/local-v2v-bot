# Architecture and extension guide

## Current V1 architecture (implemented as a scaffold)

```text
Windows browser (Gradio)
    microphone WAV/file
          |
          v
app.py: respond(audio_path, history)
    |-- faster-whisper tiny.en / CPU int8 (STT)
    |-- Ollama localhost:11434 / qwen3:0.6b (LLM)
    |-- Piper en_US-lessac-medium (TTS)
    '-- time.perf_counter() stage timing
          |
          v
Gradio transcript + text answer + WAV playback + history
```

Model objects are constructed at module import; `respond` currently owns all business logic. `gr.State` holds conversation memory in the browser session. This works for a small demo but makes headless tests difficult. The Whisper call uses `vad_filter=True` to filter the recording; it is **not** a live VAD gate.

## Proposed CPU-friendly module boundaries (future, not implemented)

```text
app.py                       Gradio UI and event binding
voice_bot/config.py          Local-first configuration + validation
voice_bot/pipeline.py        Turn orchestration and structured result
voice_bot/stt.py             Local speech transcription adapter
voice_bot/llm.py             Local Ollama adapter
voice_bot/tts.py             Piper WAV synthesis adapter
voice_bot/session.py         Bounded conversation state
voice_bot/timing.py          Stage measurements
tests/                      Dependency-free mocked core tests
```

Do not create unused abstractions: start by extracting orchestration and injecting model adapter callables in task P1.1. Introduce other modules only when a task benefits from them.

## Desired application-level contracts

`process_turn(audio_path, history)` should eventually yield a structured result such as:
- `transcript: str`
- `reply_text: str`
- `audio_path: Path | None`
- `history: list[role/content message]`
- `timings_ms: {stt, llm, tts, total}`

An orchestration result should be plain Python data, not a Gradio UI object. UI adapters map the result to components and convert exceptions into friendly errors. Keep message roles explicit (`system`, `user`, `assistant`); never treat untrusted user transcripts as system instructions. Avoid empty utterances reaching the LLM.

## Runtime boundaries and privacy

- Whisper weights, Ollama weights and Piper voices must be locally available. Validate availability before processing.
- Ollama's URL defaults to `http://127.0.0.1:11434`. Gradio binds to `127.0.0.1:7860` with `share=False`.
- Do not turn on public sharing, network-exposed interfaces, cloud APIs or analytics without explicit user approval.
- Audio inputs may be saved in local temporary locations by the UI/runtime, and output WAV files are currently created with `delete=False`. Cleanup belongs in task P1.2; do not claim that all audio is immediately deleted.
- No transcript database or cloud recording is planned for V1.

## Planned streaming design (not implemented)

```text
Mic capture -> local audio frames -> transport -> VAD/turn detector
                                      |
                                      v
                              Turn/session controller
                                      |
                                      v
                             Ollama stream -> text chunks
                                      |
                                      v
                             Piper/local TTS -> audio chunks
                                      |
                                      v
                            Playback queue (cancelable)
```

A possible local WebSocket protocol uses typed events: `session.start`, `audio.chunk`, `turn.end`, `transcript.final`, `assistant.text.delta`, `assistant.audio.chunk`, `assistant.done`, `assistant.cancel`, and `error`. **This is a design proposal, not an implemented API.** Choose PCM sample format/rate explicitly and test resampling and buffer limits.

For interruption: mark a response with a monotonically increasing turn ID; cancel or ignore output from previous turn IDs; stop client playback immediately; guard against races when TTS chunks finish late. Separate transport, session state and inference backend so the UI can later call a vLLM-Omni adapter.

## Future vLLM-Omni option

A future GPU deployment may use a supported native speech-to-speech model. Keep an adapter seam between transport/session orchestration and inference; never assume a model offers transcripts, interruption semantics, or Windows CPU compatibility simply because it supports audio. Benchmark the actual backend and only then decide on architectural migration.

## Open questions to resolve from measurements

- What is the real RAM/CPU budget while Whisper, Ollama and Piper coexist?
- Which STT size produces acceptable accuracy at acceptable speed?
- Is chunked Piper playback good enough, or is a different local TTS backend needed?
- Does Windows microphone input require resampling for streaming frames?
- What are actual turn-boundary and barge-in delays on CPU?
