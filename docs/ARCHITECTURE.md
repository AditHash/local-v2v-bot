# Architecture — Omni POC first

## Target POC (planned)

```text
Windows laptop (CPU client)        secure tunnel/WSS       Linux GPU inference
 +----------------------+     WebSocket duplex API     +----------------------+
 | recorded WAV         | --------------------------> | vLLM-Omni server     |
 | later: microphone    |  PCM input, session events  | MiniCPM-o 4.5        |
 |                      | <-------------------------- | duplex session       |
 | WAV writer / speaker |  PCM audio output, events   | speech→speech model  |
 +----------------------+                             +----------------------+
```

The **single model pipeline** performs speech understanding and speech generation. Do not call separate Whisper/Ollama/Piper in this path.

## vLLM-Omni APIs

- Duplex endpoint: `ws://HOST:8091/v1/realtime?duplex=1` (or `/v1/duplex`).
- Deploy configuration must set `session_mode: duplex`; the model's pipeline must supply a duplex plugin.
- Actual session capabilities are negotiated in `session.created.session.capabilities`.
- Typical lifecycle: connect → `session.update` → `session.created` → `input_audio_buffer.append` → `input_audio_buffer.commit` as applicable → response events including `response.output_audio.delta` → `response.done` or `response.listen` → optional accurate playback ACK → `session.close`.
- **Important:** duplex protocol and turn-based `/v1/realtime` are not interchangeable for all deployments.
- Use the official version-compatible `DuplexClient` if feasible instead of hand-rolling frame/event handling.

## Proposed project structure (not yet implemented)

```text
AGENTS.md
PLAN.md
TASKS.md
docs/OMNI_POC.md
docs/ARCHITECTURE.md
docs/PRODUCT.md
docs/TESTING.md
omni_client/
  cli.py                 WAV client / entrypoint
  audio.py               Validate PCM, chunking, WAV output
  client.py              DuplexClient transport wrapper
  metrics.py             Client timing and event summaries
tests/
  test_audio.py
  test_omni_client.py    fakes / mocked websocket, no GPU required
app.py                   LEGACY modular CPU demo (not Omni)
requirements.txt         LEGACY dependencies (not Omni client dependencies)
```

Place new client dependencies in a distinct requirements file or project metadata. The **client** must remain lightweight and CPU-capable; only the **server** needs GPU.

## Model-specific considerations

- MiniCPM-o 4.5 is the first candidate because official vLLM-Omni docs show a duplex deployment and WAV example.
- Qwen3-Omni is an optional comparison; hardware and deploy config differ.
- A duplex session may support simultaneous input/output yet not advertise all interruption controls. Feature-gate `barge-in`, playback acknowledgement, resume and transcripts.
- Model may generate encoded/raw audio chunks. Respect the negotiated output format; save a valid WAV with correct sample rate.
- State and history may be held server-side; do not inject synthetic unrelated text turns expecting native speech generation.

## Current legacy code (already committed)

`app.py` is Gradio with faster-whisper, Ollama and Piper. It is **not a vLLM-Omni implementation**. Do not refactor it as the first assignment. Once Omni works, compare latency against it if desired.

## Security / reproducibility

- Serve inference on loopback and connect over SSH tunnel or authenticated network.
- Do not open a public unauthenticated websocket server or commit real audio/voice files.
- Record server versions, model revisions, GPU specs and audio formats in test report.
- Test mocked client logic locally; run the actual model only where GPU is available.

**Details:** `docs/OMNI_POC.md`.
