from transformers import pipeline

# ✅ Use FLAN-T5 correctly (instruction-based)
text_generator = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

def generate_revision_notes(concepts, lecture_text):
    """
    Generate clear revision notes from lecture text.
    """

    if not lecture_text or len(lecture_text.strip()) < 100:
        return ["Lecture content is insufficient to generate revision notes."]

    # Limit input size
    lecture_text = lecture_text[:2500]

    prompt = (
        "Generate clear, concise revision notes for a student from the following lecture:\n\n"
        + lecture_text
    )

    try:
        output = text_generator(
            prompt,
            max_length=220,
            do_sample=False
        )

        notes_text = output[0]["generated_text"]

        # Split into readable lines
        notes = [
            line.strip()
            for line in notes_text.split(". ")
            if len(line.strip()) > 30
        ]

        return notes if notes else [notes_text]

    except Exception:
        return ["Unable to generate revision notes at this time."]
