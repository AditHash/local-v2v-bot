# vLLM-Omni speech-to-speech POC — setup and experiment

**Purpose:** validate native audio input and output with a vLLM-Omni duplex-capable model. **This experiment is not an Ollama + Whisper + Piper pipeline.**

## Development and runtime topology

```text
Windows CPU laptop                           Linux GPU host
  Python test CLI / later mic UI      WSS/SSH tunnel      vLLM-Omni
  16kHz mono PCM16 WAV  ----------------------------->  MiniCPM-o 4.5
  audio chunks / session events <---------------------  duplex session
  write WAV / play voice
```

The model runs **locally on the GPU host** and can avoid external inference APIs. If the host is rented remotely, it is **self-hosted** but **not offline on the Windows laptop**. With no GPU available, only client/protocol/mock tests can run today.

## Initial model / protocol selection

- Initial model: `openbmb/MiniCPM-o-4_5`.
- Duplex deploy config: `vllm_omni/deploy/minicpmo_4_5.yaml` (contains `session_mode: duplex`).
- WebSocket endpoint: `/v1/realtime?duplex=1` (alias `/v1/duplex`).
- Model-specific input for upstream demo: **mono PCM16, 16 kHz WAV** and reference voice WAV.
- Runtime requires a suitable **Linux GPU environment** and sufficient GPU memory; do not infer hardware compatibility just from CUDA availability. Confirm minimum GPU memory on the target release and model configuration.
- Alternative for later: Qwen3-Omni with `vllm_omni/deploy/qwen3_omni_duplex.yaml`, subject to GPU needs.

## Step A — Prepare a Linux GPU host

1. Select a self-managed Linux host with NVIDIA GPU and enough VRAM for the target model; note hourly price if rented.
2. Install drivers, Python, vLLM and matching vLLM-Omni versions **following the official installation guide for that release**. Verify `nvidia-smi` and `vllm --help`.
3. Keep Hugging Face/model storage in persistent storage if the instance may be stopped/recreated.
4. Use `--trust-remote-code` only after reviewing/trusting model code. Keep the server on loopback and access via SSH tunnel/VPN where possible.

Upstream version-sensitive installation reference:
https://docs.vllm.ai/projects/vllm-omni/en/latest/getting_started/installation/

## Step B — Serve MiniCPM-o in native duplex mode (GPU host)

From a compatible installed vLLM-Omni checkout/environment, example from official docs:

```bash
vllm serve openbmb/MiniCPM-o-4_5 --omni \
  --deploy-config vllm_omni/deploy/minicpmo_4_5.yaml \
  --trust-remote-code \
  --host 127.0.0.1 --port 8091
```

The deploy config path must exist in the chosen checkout/container. Some release docs use `vllm-omni serve` rather than `vllm serve --omni`; use the command documented for your pinned installation.

Validate `http://127.0.0.1:8091/health` and `http://127.0.0.1:8091/v1/models`, then validate a **duplex** WebSocket session. The true duplex check is the `session.created.session.capabilities` payload—not just successful TCP/WS connection.

For a local Windows-to-remote-GPU setup, an example SSH tunnel (PowerShell):

```powershell
ssh -L 8091:127.0.0.1:8091 user@gpu-host
```

Keep the tunnel open and connect client to `ws://127.0.0.1:8091/v1/realtime?duplex=1`. Substitute your actual host and credentials. Do not expose unauthenticated public WS ports.

## Step C — Run upstream WAV example first

From the version-matched upstream `vllm-omni` repository on the GPU host:

```bash
python examples/online_serving/minicpmo/realtime_duplex_demo.py \
  --url 'ws://127.0.0.1:8091/v1/realtime?duplex=1' \
  --model openbmb/MiniCPM-o-4_5 \
  --input-wav input_16k_mono.wav \
  --ref-audio reference_voice.wav \
  --output-dir /tmp/minicpmo-duplex
```

Supply actual recorded **16 kHz mono PCM16** input and a suitable reference voice WAV per the upstream example. This command is an official usage **example**, not evidence that it has been executed in this repository.

Check that audio is generated, playable, relevant to the spoken question, and not just silent/empty audio.

## Step D — Build our own lightweight client

Follow `TASKS.md` O1.1. Prefer the upstream `vllm_omni.clients.duplex.DuplexClient` with model-specific `create_duplex_session_config` and `audio_data_url`. A client on Windows should avoid installing CUDA-only server components: investigate using the upstream client-only modules and their lightweight dependencies as documented. Do **not** declare Windows installation supported until verified on Windows.

The client should:
- validate input WAV properties before sending;
- establish session and inspect capability flags;
- stream input PCM chunks and commit when required;
- receive response audio, write WAV with correct output encoding/sample rate;
- send `playback.ack` **only for audio actually played**, not just saved or received;
- cleanly close and print informative errors and observed timing.

## Protocol caveats

- vLLM-Omni has **turn-based** and **duplex** deployments. Specifying `?duplex=1` on the wrong deployment is **not** enough to make a model full duplex.
- Respect `supports_barge_in`, `supports_playback_ack`, `supports_session_resume`, etc. from the session, not hard-coded assumptions.
- Some duplex models do not expose separate STT transcripts. Don't promise a transcript UI unless the selected model emits it.
- Generated audio sample rate can differ from input rate.
- Model and release support changes; pin and note versions after actual first GPU test.

## Success criteria

- **Minimum:** native speech input → generated audible speech output through vLLM-Omni on an actual GPU server.
- **Useful:** multi-turn dialogue with clear voice quality, measured first-audio and response latencies.
- **Stretch:** microphone streaming, simultaneous listening/speaking, verified interrupts where supported.

## Authoritative references

- https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/full_duplex_api/
- https://docs.vllm.ai/projects/vllm-omni/en/latest/serving/realtime_duplex_api/
- https://docs.vllm.ai/projects/vllm-omni/en/latest/models/supported_models/
- https://docs.vllm.ai/projects/vllm-omni/en/latest/getting_started/installation/
