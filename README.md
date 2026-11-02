# local-v2v-bot — vLLM-Omni native voice-to-voice POC

**Goal:** test **vLLM-Omni native speech-to-speech** as the inference backend for a future real-time conversational voice chatbot. The intended flow is **speech input → Omni model → speech output**, **not** Whisper → Ollama → Piper.

> **Status:** planning + legacy CPU demo present. The vLLM-Omni client, GPU server validation, live streaming and barge-in are **not implemented/verified yet**. See [TASKS.md](TASKS.md) for the first Codex task.

## Why a GPU server?

The development laptop has no capable GPU. The client and mock tests can be built on Windows/CPU, but actual MiniCPM-o/vLLM-Omni inference needs a suitable **Linux GPU host**. Using a self-managed rented GPU avoids external inference APIs, but inference then runs remotely, not offline on the laptop.

## Intended POC architecture

```text
Windows laptop / Python client (WAV, later mic)
                  |
       duplex WebSocket events
                  |
                  v
       vLLM-Omni on Linux GPU
       openbmb/MiniCPM-o-4_5
       /v1/realtime?duplex=1
                  |
        generated speech chunks
                  v
         local WAV / speaker
```

Primary endpoint: `ws://127.0.0.1:8091/v1/realtime?duplex=1` when the GPU server is local or reached via SSH tunnel. The server must run a **duplex-capable model/config**, and capabilities must be verified from the session response.

The first experiment is **recorded WAV → duplex WebSocket → generated WAV**; only then build the live microphone UI and interruption support.

## Start here (Codex)

1. [AGENTS.md](AGENTS.md) — binding instructions for coding agents, goal and constraints.
2. [TASKS.md](TASKS.md) — implement task **O1.1** first: the minimal vLLM-Omni duplex WAV client and CPU-only mocked tests.
3. [PLAN.md](PLAN.md) — phased POC milestones and exit conditions.
4. [docs/OMNI_POC.md](docs/OMNI_POC.md) — server recipe, upstream demo and websocket requirements.
5. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md), [docs/PRODUCT.md](docs/PRODUCT.md), [docs/TESTING.md](docs/TESTING.md).

Suggested Codex instruction:

> Read AGENTS.md, PLAN.md, TASKS.md and docs/OMNI_POC.md. Implement O1.1 as a small Python CLI for a 16 kHz mono PCM16 WAV → vLLM-Omni MiniCPM-o duplex WebSocket → playable reply WAV. Include session-capability checks, output format handling, clear errors and mocked unit tests. Do not use Ollama/Whisper/Piper in the new path. No GPU is available locally; do not claim actual inference was tested.

## GPU server reference

On a **compatible, version-matched Linux GPU** installation:

```bash
vllm serve openbmb/MiniCPM-o-4_5 --omni \
  --deploy-config vllm_omni/deploy/minicpmo_4_5.yaml \
  --trust-remote-code --host 127.0.0.1 --port 8091
```

Run the official upstream `examples/online_serving/minicpmo/realtime_duplex_demo.py` before testing the new client. **This server command has not been executed here.** Full instructions: [docs/OMNI_POC.md](docs/OMNI_POC.md).

## Existing CPU demo (legacy / optional comparator)

The already-committed `app.py` is a **separate, push-to-talk Gradio demo** using faster-whisper → Ollama → Piper. It does **not** use vLLM-Omni and must **not** be presented as proof of native speech-to-speech. It remains available for an optional future baseline comparison.

If you want to run that legacy CPU demo on Windows:

```powershell
ollama pull qwen3:0.6b
uv python install 3.12
uv venv --python 3.12
uv pip install -r requirements.txt
.\.venv\Scripts\python.exe -m piper.download_voices en_US-lessac-medium
.\.venv\Scripts\python.exe app.py
```

Open `http://127.0.0.1:7860` and record a short English question. First-time model/voice downloads require internet. The legacy demo has **not** been verified on the user's machine.

## Upstream documentation

- [vLLM-Omni Full-Duplex API](https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/full_duplex_api/)
- [Realtime Duplex client reference](https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/realtime_duplex_api/)
- [Supported models](https://docs.vllm.ai/projects/vllm-omni/en/latest/models/supported_models/)
- [Installation](https://docs.vllm.ai/projects/vllm-omni/en/latest/getting_started/installation/)
