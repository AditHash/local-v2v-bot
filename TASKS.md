# Codex task backlog

**How to use:** complete one vertical slice at a time. Do not mark a box complete unless acceptance criteria were checked. If hardware or weights are unavailable, report that limitation and leave the relevant runtime checkbox open. Read `AGENTS.md` first.

## P0 — Validate the scaffold on Windows (highest priority)

- [ ] **P0.1 — Environment and model preflight:** confirm the documented install/launch steps work with Python 3.12, Ollama, faster-whisper, and Piper. Fix failures, update `README.md`, and add actionable missing-model/service errors.
  - Acceptance: model-not-found and Ollama-not-running errors are helpful; happy path can launch on CPU.
- [ ] **P0.2 — Real audio round trip:** capture a 3–10 second English question, transcribe it, generate a reply, and play the WAV.
  - Acceptance: one full round trip succeeds without paid API keys; note actual hardware, durations, and issues in `docs/TESTING.md`.
- [ ] **P0.3 — Conversation behavior:** confirm follow-up questions use prior context, reset clears context, blank/silent audio returns a helpful message.
  - Acceptance: three manual scenarios documented and working.
- [ ] **P0.4 — Offline check:** after the first model download, disable network access and validate inference with Ollama on localhost.
  - Acceptance: output generated and played offline; no outbound API calls required.

## P1 — First Codex implementation assignment (can start without hardware)

- [ ] **P1.1 — Extract orchestration into testable code** (**first coding assignment**).
  - Introduce a small service module (e.g., `voice_bot/pipeline.py`) with injectable STT, LLM, and TTS interfaces/callables.
  - Keep `app.py` a thin Gradio adapter; preserve existing response fields and button behavior.
  - Make model initialization lazy so importing pipeline code in a test does not download/load models.
  - Add `pytest` tests using fakes for success, missing audio, empty STT, empty LLM, multi-turn history, and failure handling.
  - **Acceptance:** tests run with no Ollama, no GPU, no mic, and no model weights; `app.py` still launches with real dependencies.
  - **Deliverable:** code + tests + updated `README.md`/`docs/TESTING.md`, with a clear statement of any real-device verification not performed.
- [ ] **P1.2 — Resource lifecycle:** remove temporary output WAV files safely after they are no longer needed; avoid deleting files before browser playback completes.
  - Acceptance: no unbounded temporary-file accumulation in repeated turns; cleanup tested.
- [ ] **P1.3 — Configuration and observability:** single config surface for model names, local Ollama host, response caps, verbosity, and model paths; monotonic stage timers.
  - Acceptance: defaults unchanged, documented, unit-tested; never log raw user audio or complete transcripts by default.
- [ ] **P1.4 — Text-only debug mode:** add a way to test Ollama response and memory without microphone or TTS.
  - Acceptance: fully local, testable without audio models, documented.
- [ ] **P1.5 — Lightweight automated checks:** install/run `pytest` and syntax/import checks; optionally add a GitHub Actions job that **does not download model weights**.
  - Acceptance: fast checks run on a clean machine without inference infrastructure.

## P2 — Streaming experiments (do not start before P0/P1 baseline)

- [ ] **P2.1:** choose and document a local audio transport; build a minimal WebSocket PCM loopback demo with explicit sample format.
- [ ] **P2.2:** VAD-driven turn boundary detection with configurable thresholds and reproducible fixtures.
- [ ] **P2.3:** stream LLM text and incrementally synthesize/play response chunks; retain push-to-talk fallback.
- [ ] **P2.4:** capture time-to-first-token, time-to-first-audio, and full turn timing.

## P3 — Full conversational behavior

- [ ] **P3.1:** session state machine and cancellation token.
- [ ] **P3.2:** interrupt speech playback when user speech begins; discard stale synthesis output.
- [ ] **P3.3:** reconnect/disconnect and cancellation race-condition tests.

## P4 — Optional GPU future work

- [ ] **P4.1:** research and document compatible vLLM-Omni models and GPU memory requirements for the deployment actually available.
- [ ] **P4.2:** implement swappable backend adapter behind the existing transport/session protocol.
- [ ] **P4.3:** benchmark modular vs native speech-to-speech using identical short prompts.

## Handoff template for every Codex task

- Task ID and what changed
- Validation run (exact commands / evidence)
- Not tested (and why)
- User-visible behavior changes
- Next unchecked task
