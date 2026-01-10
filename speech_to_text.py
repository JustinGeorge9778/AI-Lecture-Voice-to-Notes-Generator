from transformers import pipeline
import torch

stt_pipeline = pipeline(
    "automatic-speech-recognition",
    model="openai/whisper-base",
    return_timestamps=True,
    chunk_length_s=30,
    stride_length_s=5,
    device=0 if torch.cuda.is_available() else -1
)

def transcribe_audio_with_timestamps(audio_path):
    try:
        result = stt_pipeline(audio_path)

        chunks = []
        for c in result["chunks"]:
            chunks.append({
                "text": c["text"],
                "start": c["timestamp"][0],
                "end": c["timestamp"][1]
            })

        return chunks

    except Exception as e:
        raise RuntimeError(f"Speech-to-text failed: {e}")
