from transformers import pipeline
import re

# Load once
chatbot_pipeline = pipeline(
    "text2text-generation",
    model="google/flan-t5-base"
)

def is_vague_question(question: str) -> bool:
    """
    Detects vague questions like:
    'explain it', 'explain in simple', etc.
    """
    vague_patterns = [
        r"\bit\b",
        r"explain this",
        r"explain it",
        r"in simple",
        r"understandable"
    ]

    q = question.lower()
    return any(re.search(p, q) for p in vague_patterns)


def lecture_chatbot_answer(transcript: str, question: str) -> str:
    """
    Smart lecture-based chatbot.
    Handles vague questions and gives simple explanations.
    """

    # Reduce transcript size (important)
    transcript = transcript[:3000]

    if is_vague_question(question):
        prompt = f"""
You are an intelligent AI tutor.

TASK:
- The user asked a vague question.
- First, identify the MOST IMPORTANT concept in the lecture.
- Then explain that concept in SIMPLE and UNDERSTANDABLE terms.
- Use ONLY the lecture content.
- Do NOT say you are an AI.
- Do NOT refuse.

LECTURE:
{transcript}

USER QUESTION:
{question}

ANSWER (simple explanation):
"""
    else:
        prompt = f"""
You are an AI study assistant.

RULES:
- Answer using ONLY the lecture content.
- Explain in SIMPLE and CLEAR language.
- If the answer is not found, say:
  "This topic is not clearly explained in the lecture."

LECTURE:
{transcript}

QUESTION:
{question}

ANSWER:
"""

    result = chatbot_pipeline(
        prompt,
        max_length=220,
        do_sample=True,
        temperature=0.5
    )

    return result[0]["generated_text"].strip()
