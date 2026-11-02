# Instructions for Codex and other coding agents

This is the repository-level source of coding guidance. Read `README.md`, `PLAN.md`, `TASKS.md`, and `docs/ARCHITECTURE.md` before implementing changes. `docs/PRODUCT.md` describes the intended behavior; `docs/TESTING.md` describes how to verify it.

## Mission and constraints

Build an **entirely local, CPU-first voice-to-voice chatbot POC** that can later evolve into an interruptible, real-time voice agent. The user's current machine has **no usable NVIDIA GPU**; a working GPU must never be required for the initial stages.

- Current V1 stack: Python 3.12, Gradio, faster-whisper (`tiny.en`, CPU/int8), Ollama (`qwen3:0.6b`), Piper (`en_US-lessac-medium`).
- Inference stays local. No paid APIs, hosted transcription, hosted TTS, telemetry, or cloud dependencies in the default path.
- Internet access **is allowed during initial installation/model download**, but the running chatbot must work after downloads with internet disconnected.
- Development OS is Windows/PowerShell; keep paths, subprocess behavior, and examples compatible with Windows. Cross-platform support is a plus.
- The MVP is English-only and push-to-talk. Do **not** describe it as live/full-duplex until that capability has been implemented and demonstrated.
- Future vLLM-Omni integration is optional and GPU-dependent; do not make it a prerequisite for the CPU POC.

## Current repository reality

- `app.py` is the initial, mostly single-file Gradio application. It loads model objects at import, transcribes an audio file, calls Ollama, synthesizes WAV via Piper, returns speech/text/history/timings.
- `requirements.txt` contains broad dependency ranges; there is no automated test suite, CI, package layout, VAD-triggered live conversation, or model download automation yet.
- `vad_filter=True` in offline Whisper transcription does **not** mean that streaming endpoint detection or barge-in works.
- The whole pipeline has **not** been runtime-tested on the user's Windows machine. Do not claim verified audio quality, latency, or offline operation without testing.

## Working agreement

1. Pick the **first uncompleted task** in `TASKS.md` (or a task explicitly assigned by the user). Deliver the smallest independently testable slice. Avoid broad rewrites.
2. Explain what you're changing, then modify code and tests. Preserve the ability to run `python app.py`.
3. Use clear boundaries for STT, LLM, TTS, UI/session state, and timing. Favor plain Python and explicit functions over unnecessary agent frameworks.
4. Keep local/offline behavior the default. If any optional network service, model, or new dependency is introduced, explain its purpose and make it opt-in.
5. Never embed API credentials, private audio/transcripts, personally identifying content, or downloaded model weights in the repository.
6. Prefer dependency injection/lazy model initialization so pure unit tests can run **without** downloaded weights, microphone hardware, or a running Ollama instance.
7. Use bounded history, bounded generated response length, and clear user-facing errors. Avoid leaving temporary WAV files indefinitely.
8. Do not silently change the model defaults, UI behavior, or platform support. Document new config variables and update the relevant docs.
9. Add or update tests for changed logic, run what is possible locally, and report explicitly what was **not** tested (especially real audio and model inference).
10. After implementing, update the checkboxes in `TASKS.md`, and update `PLAN.md` only when a milestone's status truly changes. Keep docs in sync with actual code.

## Project conventions

- Python: 3.12, type hints, small composable modules, standard logging (avoid logging transcripts by default).
- No mandatory Docker, database, Redis, LangChain, paid services, or remote hosted LLMs for V1.
- Prefer `pytest` for tests. Keep tests deterministic with mocks/fakes; integration tests are optional and should be explicitly marked or documented.
- For experimental streaming, label new protocols/configs as proposals until implemented; prefer WebSocket first, WebRTC only when its complexity is justified.
- Don't over-promise latency: record actual STT, LLM, TTS, first-audio, and end-to-end timings on the test machine before selecting targets.

## Commands to preserve (PowerShell)

```powershell
ollama pull qwen3:0.6b
uv python install 3.12
uv venv --python 3.12
uv pip install -r requirements.txt
.\.venv\Scripts\python.exe -m piper.download_voices en_US-lessac-medium
.\.venv\Scripts\python.exe app.py
```

If you introduce a new test dependency, document the install and run commands in `README.md` and `docs/TESTING.md`.

## Definition of a complete coding task

- Acceptance criteria in `TASKS.md` are met and checked off only with evidence.
- Offline/local-first defaults remain intact.
- Static checks/tests you can execute pass; any failures or unrun checks are disclosed.
- User-facing run instructions remain accurate.
- Summary identifies changed files, how to run/test, known limitations, and the next task.
