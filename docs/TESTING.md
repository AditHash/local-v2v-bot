# Test plan — native vLLM-Omni

This is an **unverified POC**. As of this documentation update, no GPU or running vLLM-Omni inference server was provided. The original CPU Ollama demo does not count toward Omni success.

## A. CPU-only client tests (can run now, once Codex implements O1.1)

- [ ] Validate correct 16 kHz mono PCM16 WAV passes input checks.
- [ ] Reject invalid encoding/channels/sample rates with clear remediation.
- [ ] Mock a duplex session handshake and verify capability interpretation.
- [ ] Mock input streaming/commit and response audio chunks.
- [ ] Reassemble output into a valid WAV using correct rate/format.
- [ ] Test error events, disconnects, timeouts and session.close cleanup.
- [ ] Test no dependency on Ollama, Whisper, Piper, CUDA or paid inference APIs.

Planned command (only after tests/dependencies are added):

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Mock tests prove **client behavior only**.

## B. Real vLLM-Omni GPU validation (required for actual POC)

- [ ] Record GPU host, VRAM, Linux distribution, driver/CUDA, Python, vLLM and vLLM-Omni versions.
- [ ] Serve `openbmb/MiniCPM-o-4_5` with `minicpmo_4_5.yaml` in `duplex` mode.
- [ ] Confirm server health/model listing and WebSocket `session.created.session.capabilities`.
- [ ] Run the **upstream** recorded WAV duplex demo and save generated audio.
- [ ] Verify audible reply is relevant, nonempty and not silence.
- [ ] Run our Codex client against the same server and compare results.
- [ ] Test follow-up turn and conversation continuity.
- [ ] Observe server memory/VRAM and note any out-of-memory/timeout errors.
- [ ] Record client→server network RTT when testing from a remote laptop.

## C. Streaming/interruptions (after B passes)

- [ ] Mic capture → PCM frames → live duplex endpoint.
- [ ] Generated audio starts before full response completes.
- [ ] Measure time to first audio heard and end-to-end latency.
- [ ] Verify ACK is sent for audio **played** and not just buffered.
- [ ] Attempt barge-in **only if** `supports_barge_in` is advertised, and record whether it works.
- [ ] Test drop/reconnect when server capability permits.

## Measurements — fill only after observing

| Date | Model | GPU / VRAM | Input duration | First audio ms | Total response ms | Quality notes | Remote RTT |
| --- | --- | --- | --- | ---: | ---: | --- | ---: |
| Pending | MiniCPM-o 4.5 | Not available | — | — | — | Not tested | — |

## Evidence to capture (keep user speech private)

- Git commit and pinned server/client model versions
- Execution commands and environment summary
- Success/failure and error messages without secrets
- Duration and GPU memory utilization
- Session flags and actual capabilities
- Locally stored example output WAV (not committed by default)

## POC decision

Do not declare native vLLM-Omni voice chat validated until B succeeds on real GPU inference. Mocked tests, offline WAV processing with other libraries, and a successful WebSocket TCP handshake are insufficient.

For setup commands see `docs/OMNI_POC.md`.
