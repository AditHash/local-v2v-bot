# Codex instructions — vLLM-Omni Voice-to-Voice POC

**Read this file first.** Then read `README.md`, `PLAN.md`, `TASKS.md`, `docs/OMNI_POC.md`, `docs/ARCHITECTURE.md`, and `docs/TESTING.md` before making edits.

## Objective (do not reinterpret)

The primary POC is to **evaluate vLLM-Omni as the speech-to-speech engine for a conversational voice chatbot**, using a model that accepts speech/audio and emits generated speech/audio through vLLM-Omni's realtime duplex API. The POC must prove that speech goes **directly through an Omni model**, not through separate Whisper → text LLM → Piper services.

- Target inference server: **vLLM-Omni**, initial model **`openbmb/MiniCPM-o-4_5`** with the upstream duplex deployment; evaluate Qwen3-Omni as a later alternative if hardware allows.
- Target protocol: **`WS /v1/realtime?duplex=1`**, with `session_mode: duplex`, model capability negotiation, PCM audio input, audio output, turn/session handling and playback acknowledgement where supported.
- User **has no capable local GPU**. Develop the client and mocked tests on Windows/CPU. Actual Omni model inference must run on a suitable Linux GPU machine (a rented GPU instance is acceptable for a POC). A remotely hosted self-managed GPU is not the same as entirely offline/local inference.
- **No paid inference APIs** (OpenAI/Gemini/ElevenLabs) in the Omni path. Self-managed GPU infrastructure may cost money.
- Maintain `app.py` (Gradio + faster-whisper + Ollama + Piper) as an optional **legacy modular baseline**. It is not the target POC and cannot satisfy any Omni acceptance criterion.
- Do not make Ollama, faster-whisper or Piper a dependency of the new Omni client or verification tests.
- Initial success criteria: WAV file → vLLM-Omni duplex WebSocket → generated playable audio; then live mic/speaker; then meaningful interruptions only where the selected model explicitly supports them.

## Development approach

1. Begin with the **first unchecked Omni task** in `TASKS.md`. Deliver one small, testable slice before building an elaborate UI.
2. **First task (O1.1):** create a testable Python client/CLI that speaks the actual duplex protocol with a recorded **16 kHz mono PCM16 WAV**, using upstream `vllm_omni.clients.duplex.DuplexClient` where practical. Preserve event/turn boundaries and capture received audio. Provide fake/mock transport tests that run CPU-only.
3. The client runs on the user's Windows CPU; the inference server runs on Linux + compatible GPU. Allow a configurable WebSocket URL and model. Never require CUDA or server packages to run the client tests.
4. Prefer upstream client helpers/model presets to custom protocol reconstruction. If using raw WebSockets, follow upstream event schema exactly; do not invent method names or event fields.
5. Treat `session.created.session.capabilities` as authoritative. Don't assume every model supports `barge-in`, transcripts, playback ACKs, session resume or multi-session.
6. Handle audio formats explicitly: PCM sample rate, bit depth, mono/channel count, chunk boundaries, sample encoding and output WAV container metadata. Avoid assuming output format equals input format.
7. Protect privacy: don't commit microphone recordings, generated user audio, voice reference WAVs, downloaded models, tokens, secrets or private logs. Store demo outputs in a gitignored local directory.
8. For remote testing, favor SSH tunneling, VPN or authenticated WSS; do not publish an unauthenticated GPU WebSocket on the public internet.
9. Log timing and event names by default, **not** full transcripts or audio. Distinguish end-to-end latency from server inference latency; include network RTT in remote results.
10. Keep `README.md`, `PLAN.md`, `TASKS.md`, and `docs/TESTING.md` accurate. Do not mark GPU inference as verified until an actual model has been served and tested.
11. Use Python 3.12, straightforward modules, type hints, and `pytest` with mock transports. Avoid new frameworks unless indispensable for the experiment.
12. State exactly what tests ran, what requires a GPU, and what remains unverified.

## Technical source of truth

- Full-duplex overview: https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/full_duplex_api/
- Duplex client and wire reference: https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/realtime_duplex_api/
- Supported models: https://docs.vllm.ai/projects/vllm-omni/en/latest/models/supported_models/
- Installation: https://docs.vllm.ai/projects/vllm-omni/en/latest/getting_started/installation/

The upstream project evolves quickly: check current documentation against the **specific installed release/checkout**, rather than assuming examples from another version are compatible.

## Acceptance definition

An Omni task is complete only when its acceptance checks are met. Mocked client tests prove transport/client logic only; **they do not prove vLLM-Omni speech generation**. When there's no GPU, implement and test the client now and leave the actual GPU validation checklist unchecked.

### Starter prompt for Codex

> Read AGENTS.md, PLAN.md, TASKS.md and docs/OMNI_POC.md. Implement task O1.1: a minimal testable vLLM-Omni duplex WAV client targeting MiniCPM-o 4.5, with configurable WebSocket URL/model, audio format validation, output audio WAV, capability logging, error handling, and mock tests that run without a GPU. Do not use Ollama/Whisper/Piper in this path. Do not claim the model ran unless tested against a GPU server.
