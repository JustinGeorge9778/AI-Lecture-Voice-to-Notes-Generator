import nltk
from nltk.tokenize import sent_tokenize
from transformers import pipeline

# Download tokenizer once
nltk.download("punkt", quiet=True)

# Lightweight model for concept extraction
concept_model = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

def extract_concepts(text, max_concepts=5):
    """
    Extracts key concepts/topics from lecture text.
    Returns a list of short concept strings.
    """

    # Reduce input size (important for performance)
    sentences = sent_tokenize(text)
    short_text = " ".join(sentences[:10])

    prompt = f"""
Extract {max_concepts} important key concepts or topics
from the lecture content below.
Return only the concept names as a list.

LECTURE:
{short_text}

CONCEPTS:
"""

    try:
        output = concept_model(
            prompt,
            max_length=120,
            do_sample=False
        )[0]["generated_text"]

        # Clean output
        concepts = [
            c.strip("•-1234567890. ")
            for c in output.split("\n")
            if len(c.strip()) > 3
        ]

        return concepts[:max_concepts]

    except Exception:
        # Fallback: return sentence-based concepts
        return sentences[:max_concepts]
