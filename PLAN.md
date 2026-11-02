# Plan — evaluate vLLM-Omni for a voice-to-voice chatbot

## Single goal

Demonstrate **native speech input → vLLM-Omni speech-capable model → generated speech output**, and determine whether full-duplex serving is viable for a future voice chatbot.

The previous CPU **Whisper → Ollama → Piper** app is **not the primary POC**. It remains as a control/baseline, but will not be a prerequisite or substitute for native Omni testing.

## Constraints / strategy

- Development laptop: Windows without a capable GPU. Test UI/client/protocol handling with mocks and fixtures locally.
- Inference: use a **self-managed Linux GPU host** when available. This can be on-prem or a temporary rented GPU. Avoid paid third-party model APIs. Remote hosting is self-hosted but **not physically local/offline**.
- First model: `openbmb/MiniCPM-o-4_5` with duplex config `vllm_omni/deploy/minicpmo_4_5.yaml`. Confirm model and hardware compatibility on the actual host.
- Protocol: `/v1/realtime?duplex=1`; verify `session.created.session.capabilities` before relying on overlap, playback ACK and interruptions.

## O0 — Grounded server recipe and experiment design

**Status: Documented; GPU execution pending.**

- [ ] Choose a specific Linux GPU host, CUDA/driver versions, available VRAM and disk, and pinned vLLM + vLLM-Omni versions.
- [ ] Confirm model weight license/terms, download size, dependencies and actual memory use.
- [ ] Start duplex server using the **matching upstream release**.
- [ ] Confirm `/health`, `/v1/models` and a duplex WebSocket handshake with capability fields.
- [ ] Run the upstream `realtime_duplex_demo.py` using a 16 kHz mono PCM16 input WAV and any required reference voice audio.

**Exit:** official sample yields audible response on the GPU server; collect setup steps and timings.

## O1 — Minimum independent Omni client (first Codex work)

**Status: Planned; can be developed CPU-only.**

- Build simple Python CLI accepting input WAV, WebSocket URL, model ID, optional reference voice and output directory.
- Use official `DuplexClient`/MiniCPM-o preset if feasible; otherwise implement a wire-compatible client with tests.
- Wait for valid session and capability negotiation. Stream correctly encoded audio, handle generated audio events, and write playable audio plus summary metadata.
- Add fake-transport tests, timeouts and error diagnostics. Allow the **client** to run on Windows without server-side GPU packages.
- Validate against the real server once O0 infrastructure exists.

**Exit:** first recorded voice question goes through vLLM-Omni and produces spoken response. Mock tests alone are not the exit criterion.

## O2 — Live microphone and speaker POC

**Status: Planned.**

- Capture and resample microphone audio at client side.
- Stream continuously to Omni; play returned audio as chunks arrive.
- Show live connection state, session events and optional model-provided transcripts.
- Keep existing WAV CLI for reproducible tests.
- Collect time-to-first-audio, end-to-end latency, glitches and network conditions.

**Exit:** repeatable live two-way audio in a local browser or desktop client connected to self-hosted vLLM-Omni.

## O3 — Evaluate real-time behavior

**Status: Planned.**

- Test simultaneous input/output, model-triggered turn transitions, overlapping speech and interruption.
- Use capability flags; report 'unsupported' rather than simulating model support.
- Send playback acknowledgements for audio actually played, not merely received or buffered.
- Test session reconnection/close, buffer sizing, backpressure and multi-turn consistency.

**Exit:** documented demonstration or limitation of full-duplex behavior on the selected model.

## O4 — Compare alternatives and make decision

**Status: Planned.**

- Benchmark MiniCPM-o vs a compatible Qwen3-Omni deployment (if sufficient GPU available).
- Compare with optional legacy modular Ollama/Whisper/Piper only as a baseline for latency, robustness and quality.
- Report GPU/VRAM usage, setup complexity, response quality, interruption support, and per-minute infrastructure costs using *actual measurements*.
- Decide whether to pursue a production voice agent with vLLM-Omni.

**Exit:** an evidence-based recommendation, not just a working UI.

**Read:** `TASKS.md`, `docs/OMNI_POC.md`, `docs/ARCHITECTURE.md`, `docs/TESTING.md`.
