"""CPU-only, push-to-talk local voice chatbot proof of concept."""

import os
import tempfile
import time
import wave
from pathlib import Path

import gradio as gr
from faster_whisper import WhisperModel
from ollama import Client
from piper import PiperVoice

ROOT = Path(__file__).resolve().parent
VOICE_MODEL = ROOT / "en_US-lessac-medium.onnx"
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:0.6b")
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny.en")

SYSTEM_PROMPT = (
    "You are a helpful voice assistant. Keep answers short, conversational, "
    "and easy to understand when spoken aloud. Avoid markdown formatting."
)

if not VOICE_MODEL.exists():
    raise SystemExit(
        f"Missing {VOICE_MODEL.name}. Download it using:\n"
        "  python -m piper.download_voices en_US-lessac-medium\n"
        "from this project's directory."
    )

print(f"Loading Whisper {WHISPER_MODEL} in CPU/int8 mode...")
stt = WhisperModel(
    WHISPER_MODEL,
    device="cpu",
    compute_type="int8",
    cpu_threads=min(os.cpu_count() or 4, 4),
)
print("Loading Piper voice...")
tts = PiperVoice.load(VOICE_MODEL)
ollama = Client(host=os.getenv("OLLAMA_HOST", "http://127.0.0.1:11434"), timeout=180)


def respond(audio_path: str | None, history: list[dict] | None):
    """Record -> STT -> LLM -> TTS. history contains user/assistant messages."""
    history = list(history or [])
    if not audio_path:
        raise gr.Error("Record a message with the microphone first.")

    try:
        start = time.perf_counter()
        segments, _ = stt.transcribe(
            audio_path,
            language="en",
            beam_size=1,
            vad_filter=True,
        )
        transcript = " ".join(segment.text.strip() for segment in segments).strip()
        stt_s = time.perf_counter() - start
        if not transcript:
            raise gr.Error("No speech was detected. Please record again.")

        start = time.perf_counter()
        # Keep just the 10 most recent chat messages to minimize CPU inference cost.
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            *history[-10:],
            {"role": "user", "content": transcript},
        ]
        result = ollama.chat(
            model=LLM_MODEL,
            messages=messages,
            think=False,
            options={"num_predict": 120, "num_ctx": 2048, "temperature": 0.6},
        )
        reply = (result.message.content or "").strip()
        llm_s = time.perf_counter() - start
        if not reply:
            raise gr.Error("Ollama returned an empty answer. Try again.")

        start = time.perf_counter()
        with tempfile.NamedTemporaryFile(prefix="voice-poc-", suffix=".wav", delete=False) as tmp:
            output_path = Path(tmp.name)
        with wave.open(str(output_path), "wb") as wav_file:
            tts.synthesize_wav(reply, wav_file)
        tts_s = time.perf_counter() - start

        new_history = [
            *history,
            {"role": "user", "content": transcript},
            {"role": "assistant", "content": reply},
        ]
        # Gradio chatbot shows the whole session; the LLM uses a sliding window.
        timings = (
            f"STT: {stt_s:.1f}s | LLM: {llm_s:.1f}s | "
            f"TTS: {tts_s:.1f}s | Total: {stt_s + llm_s + tts_s:.1f}s"
        )
        return transcript, reply, str(output_path), new_history, new_history, timings
    except gr.Error:
        raise
    except Exception as exc:
        raise gr.Error(
            "Processing failed. Check that Ollama is running and that "
            f"'{LLM_MODEL}' has been downloaded. Details: {exc}"
        ) from exc


def clear_conversation():
    return "", "", None, [], [], ""


with gr.Blocks(title="Offline Voice Chatbot — CPU POC") as demo:
    gr.Markdown(
        "# Offline Voice Chatbot\n"
        "**Record → Whisper (CPU) → Ollama → Piper (CPU) → Listen**\n\n"
        "This is a *push-to-talk POC*, not continuous live speech-to-speech. "
        "All inference stays on this machine after model downloads."
    )
    with gr.Row():
        mic = gr.Audio(
            sources=["microphone"],
            type="filepath",
            label="1. Record your question, then stop recording",
        )
        audio_out = gr.Audio(label="3. Assistant voice", autoplay=True, interactive=False)

    with gr.Row():
        send = gr.Button("2. Ask the assistant", variant="primary")
        clear = gr.Button("Clear conversation")

    transcript_out = gr.Textbox(label="You said", interactive=False)
    reply_out = gr.Textbox(label="Assistant replied", interactive=False)
    stats_out = gr.Textbox(label="Processing time", interactive=False)
    chat = gr.Chatbot(label="Conversation", type="messages")
    memory = gr.State([])

    send.click(
        fn=respond,
        inputs=[mic, memory],
        outputs=[transcript_out, reply_out, audio_out, chat, memory, stats_out],
        concurrency_limit=1,
    )
    clear.click(
        fn=clear_conversation,
        inputs=None,
        outputs=[transcript_out, reply_out, audio_out, chat, memory, stats_out],
    )

if __name__ == "__main__":
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
