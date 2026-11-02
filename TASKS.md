# Codex backlog — native vLLM-Omni speech-to-speech

**Primary purpose:** evaluate vLLM-Omni. The existing `app.py` (Ollama/Whisper/Piper) is a legacy CPU baseline and does **not** satisfy the target POC. Do tasks in order unless the user explicitly chooses otherwise.

## O1 — Client development without a GPU (start here)

- [ ] **O1.1 — First implementation task: duplex WAV client.**
  - Implement `omni_client/` or `clients/` with a CLI that reads a **16 kHz mono PCM16 WAV** and talks to a configurable vLLM-Omni server over `/v1/realtime?duplex=1`.
  - Use `DuplexClient` and `create_duplex_session_config` from the version-matched upstream client package where practical; minimize reimplemented protocol.
  - Require model ID (default `openbmb/MiniCPM-o-4_5`), WebSocket URL, output directory, and optional reference voice WAV as applicable to MiniCPM-o.
  - Handle session handshake, advertised capabilities, audio append/commit, responses/audio, playback ACK only when meaningful, errors, and close.
  - Persist a **playable WAV** synthesized from returned audio according to the server's actual output sample rate/encoding; never concatenate encoded chunks blindly.
  - Provide clean errors for missing input file, unsupported sample format, wrong endpoint/server mode, WebSocket failure and timeout.
  - Add offline `pytest` tests for audio format validation, mocked session/events, audio output assembly, error propagation and teardown. The client/test environment must not import CUDA-only server machinery.
  - **Acceptance (code):** mock tests pass on Windows CPU, documented CLI command, nothing requires Ollama/STT/TTS APIs.
  - **Acceptance (real POC):** a real GPU-hosted MiniCPM-o run produces audible speech and the session capabilities are logged. Leave this box unchecked if only mock tests run.
- [ ] **O1.2 — Protocol observability:** record session ID/capabilities and per-turn timestamps in local optional JSON summary (no private audio/transcripts logged by default).
- [ ] **O1.3 — Document/setup reproducibility:** pin compatible client/server version, sample rate, reference voice constraints, and an input WAV fixture recipe.

## O0 — GPU host/server validation (requires GPU)

- [ ] **O0.1:** record GPU type, VRAM, available disk, OS, CUDA and versions in `docs/TESTING.md`.
- [ ] **O0.2:** deploy Linux vLLM-Omni and MiniCPM-o 4.5 with `session_mode: duplex` as in `docs/OMNI_POC.md`.
- [ ] **O0.3:** verify duplex handshake **with capability flags**, not just a 101 WebSocket status.
- [ ] **O0.4:** execute upstream `realtime_duplex_demo.py` with actual 16 kHz mono PCM16 WAV; save generated playable audio outside git.
- [ ] **O0.5:** execute new O1 client against server and compare outputs, errors and timings.

## O2 — Live voice chatbot (after verified WAV path)

- [ ] **O2.1:** local mic capture, normalization/resampling and streaming to self-hosted Omni.
- [ ] **O2.2:** audio output playback queue, correct sample format and progressive playback.
- [ ] **O2.3:** session event/status and optional text from Omni (only if provided by model).
- [ ] **O2.4:** record end-to-end and time-to-first-audio latencies with local vs remote attribution.

## O3 — Duplex and interruptions

- [ ] **O3.1:** test concurrent listening/speaking; capability-gated behavior only.
- [ ] **O3.2:** implement barge-in when supported; stop audio, cancel/stale-event fence, ACK/truncation according to protocol.
- [ ] **O3.3:** test reconnect, close, buffering and backpressure.
- [ ] **O3.4:** write limitations and real GPU observations, not assumptions.

## O4 — Optional evaluation

- [ ] **O4.1:** assess Qwen3-Omni full-duplex with compatible GPU budget and deployment config.
- [ ] **O4.2:** compare against the modular legacy CPU app as optional baseline.
- [ ] **O4.3:** recommendation from measured quality, latency, GPU memory and implementation complexity.

## Every Codex delivery must report

- Task(s) completed and code/doc files changed
- Exact tests executed; mocked vs real GPU distinguished
- Playback/audio output verification
- GPU limitations or blockers and next task
- No third-party paid inference API used

Official references and starting recipe are in `docs/OMNI_POC.md`.
