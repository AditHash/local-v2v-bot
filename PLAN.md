# Implementation plan — local-v2v-bot

**North star:** a private voice assistant that listens, responds naturally in speech, and can eventually be interrupted mid-answer. **Near-term constraint:** no GPU, Windows laptop, minimal memory consumption and no paid inference APIs.

Status terms: **Scaffolded** means source exists but was not validated with real devices; **Planned** means not implemented. Only mark **Verified** after an actual successful local test.

## Phase 0 — Validate current push-to-talk POC (next)

**Status: Scaffolded; runtime verification pending.**

- Install dependencies and weights following `README.md`.
- Make a successful short microphone → transcript → Ollama answer → synthesized audio round trip.
- Test multi-turn memory and clear-conversation behavior.
- Record STT, LLM, TTS, and total latency plus CPU/RAM observations.
- Fix any installer, audio encoding, Windows temporary-file, or Ollama compatibility issues uncovered.

**Exit condition:** a reproducible Windows CPU run with no cloud inference, plus documented results and known limitations.

## Phase 1 — Make the CPU baseline robust and testable

**Status: Planned. See `TASKS.md` for the first coding slice.**

- Extract testable STT/LLM/TTS orchestration from `app.py` with lazy loading or dependency injection; keep Gradio UX intact.
- Add deterministic tests, error handling, structured timing, and bounded conversation memory.
- Provide explicit offline mode preflight checks, model missing diagnostics, and temporary audio cleanup.
- Add optional text-only smoke test to debug Ollama independently of microphone/audio devices.
- Establish a small release/test checklist.

**Exit condition:** core orchestration unit-tested without weights/hardware; end-to-end workflow still runnable.

## Phase 2 — Lower perceived latency / streaming POC

**Status: Planned, must remain viable without GPU.**

- Evaluate WebSocket-based local mic streaming with a **small proof**; retain the push-to-talk fallback.
- Add audio capture buffering and speech end detection (VAD). Be explicit about sample rate, mono PCM, buffering, silence thresholds, and UX.
- Stream Ollama tokens and split replies into speech-friendly chunks for TTS.
- Start speech playback before the full answer finishes where feasible.
- Capture time-to-first-token, time-to-first-audio and full-turn latency.
- Investigate CPU load / scheduling contention; never claim real-time performance without measurements.

**Exit condition:** a local demo showing partial response playback and metrics, with deterministic unit tests for stream/turn handling.

## Phase 3 — Natural conversation / interruptions

**Status: Planned.**

- Implement a bounded session state machine (idle → listening → processing → speaking → interrupted).
- Detect when a user begins speaking during audio playback.
- Cancel or discard pending LLM/TTS work, stop queued playback, and start the next turn without stale audio.
- Make cancel/session lifecycle explicit; add concurrency, race-condition, and reconnect tests.
- Consider WebRTC/LiveKit only if measurable benefit outweighs the additional complexity.

**Exit condition:** reliable interruption demo, with observed limitation notes for CPU-only hardware.

## Phase 4 — Optional native speech-to-speech experiment

**Status: Research only; GPU not currently available.**

- On suitable GPU infrastructure, evaluate vLLM-Omni and a compatible speech-in/speech-out model.
- Keep the transport/UI independent of inference backend; introduce a model adapter rather than replacing the CPU implementation.
- Compare quality, speech round-trip latency, memory, interruptions, and transcription visibility.
- Decide from measurements whether to keep modular STT→LLM→TTS or add an Omni backend.

**Exit condition:** optional benchmark and recommendation; CPU path continues to work.

## Priority and scope boundaries

Priority: **get the existing POC working** → **make it testable** → **measure** → **stream** → **interruptions** → **optional GPU comparison**.

Out of scope for now: commercial telephony integration, speaker verification, RAG, SaaS auth, storing audio/transcripts, production multi-tenancy, self-hosted vLLM on unsupported CPU hardware, and a full React rewrite.

See `docs/PRODUCT.md` for requirements, `docs/ARCHITECTURE.md` for current/planned boundaries, and `docs/TESTING.md` for verification.
