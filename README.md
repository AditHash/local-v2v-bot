# local-v2v-bot

**Offline voice-to-voice chatbot POC that runs on a CPU.**

Record speech in your browser, transcribe it locally, get an answer from a local Ollama model, and synthesize a spoken reply—all without cloud inference APIs.

## Stack

- **STT:** [faster-whisper](https://github.com/SYSTRAN/faster-whisper) with `tiny.en` and CPU INT8
- **LLM:** [Ollama](https://ollama.com/) with `qwen3:0.6b`
- **TTS:** [Piper](https://github.com/OHF-Voice/piper1-gpl) with `en_US-lessac-medium`
- **Web UI:** [Gradio](https://www.gradio.app/)

This **V1** is push-to-talk (record → stop → ask → listen), **not** continuous full-duplex speech-to-speech or vLLM-Omni. All inference can run offline once model weights are downloaded.

## Quick start: Windows PowerShell

Install [Ollama](https://ollama.com/download) and [uv](https://docs.astral.sh/uv/getting-started/installation/). Start the Ollama application, then:

```powershell
git clone https://github.com/AditHash/local-v2v-bot.git
cd local-v2v-bot
ollama pull qwen3:0.6b

uv python install 3.12
uv venv --python 3.12
uv pip install -r requirements.txt

# Download Piper voice model and its config to the project folder:
.\.venv\Scripts\python.exe -m piper.download_voices en_US-lessac-medium

# Start the application:
.\.venv\Scripts\python.exe app.py
```

Open **http://127.0.0.1:7860**. Allow microphone access, record a short question, stop recording and click **Ask the assistant**.

On the first run, faster-whisper downloads Whisper weights. Internet is required for initial package/model downloads only. No cloud inference account or key is needed.

## Architecture

```text
Browser microphone (push to talk)
        |
        v
Gradio app
        |
        v
faster-whisper tiny.en [CPU STT]
        |
        v
Ollama qwen3:0.6b [CPU LLM]
        |
        v
Piper en_US-lessac-medium [CPU TTS]
        |
        v
Browser audio player
```

The app also shows the recognized text, assistant response, conversation history, and timings for each stage.

## Configuration

Optional overrides in PowerShell:

```powershell
# Higher quality STT (slower):
$env:WHISPER_MODEL="base.en"

# Larger LLM (slower, more RAM):
ollama pull qwen3:1.7b
$env:OLLAMA_MODEL="qwen3:1.7b"

# If Ollama listens on a nondefault address:
$env:OLLAMA_HOST="http://127.0.0.1:11434"

.\.venv\Scripts\python.exe app.py
```

The default pipeline is English-only. To use other languages, switch to a multilingual Whisper model, remove/change the `language="en"` argument in `app.py`, and download a suitable Piper voice.

## Troubleshooting

- **Ollama connection error:** ensure Ollama is running on port 11434.
- **Ollama model not found:** run `ollama pull qwen3:0.6b`.
- **Missing Piper model:** rerun `python -m piper.download_voices en_US-lessac-medium` using the project's Python environment and from the repository directory.
- **Browser microphone disabled:** allow microphone permission for `127.0.0.1`.
- **Slow responses:** keep `tiny.en` / `qwen3:0.6b` on older CPUs, close memory-intensive apps and reduce `num_predict`.
- **Audio doesn't autoplay:** press Play manually; browser autoplay restrictions vary.
- **Generated WAV files:** temporary output files accumulate in your system temp directory; cleanup is not implemented in V1.

## Next milestones

1. Measure end-to-end and per-stage latency on your machine.
2. Add VAD / automatic turn detection.
3. Stream partial text and synthesized audio.
4. Add interruption / barge-in and WebSocket or WebRTC transport.
5. Experiment with vLLM-Omni native speech-to-speech when a suitable GPU is available.

This is a development POC, not a production-ready voice agent.

## Development with Codex

Codex should start with [AGENTS.md](AGENTS.md), then use the following source-of-truth documents:

- [PLAN.md](PLAN.md) — milestone roadmap and exit criteria
- [TASKS.md](TASKS.md) — ordered implementation backlog and first coding assignment
- [docs/PRODUCT.md](docs/PRODUCT.md) — product scope and acceptance criteria
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — current design and planned module boundaries
- [docs/TESTING.md](docs/TESTING.md) — manual checks and test strategy

**Suggested first Codex prompt:** "Read AGENTS.md, PLAN.md, TASKS.md and the docs/ directory. Implement P1.1 as the smallest testable refactor without changing the CPU-only V1 user experience. Add mocked pytest tests, update docs and report exactly what was/was not tested."
