import os
import requests
import random

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
HF_API_TOKEN = os.getenv("HF_API_TOKEN")
MODEL_URL = "https://api-inference.huggingface.co/models/google/flan-t5-base"

HEADERS = {
    "Authorization": f"Bearer {HF_API_TOKEN}",
    "Content-Type": "application/json"
}

# -------------------------------------------------
# HF API CALL
# -------------------------------------------------
def hf_generate(prompt, max_tokens=200):
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": max_tokens,
            "temperature": 0.7
        }
    }

    response = requests.post(MODEL_URL, headers=HEADERS, json=payload)
    response.raise_for_status()

    return response.json()[0]["generated_text"].strip()

# -------------------------------------------------
# QUIZ (SHORT QUESTIONS)
# -------------------------------------------------
def generate_quiz_questions(text, num_questions=5):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 40]
    random.shuffle(sentences)

    questions = []

    for sent in sentences[:num_questions]:
        prompt = f"""
Generate ONE short quiz question from the content below.
Content: "{sent}"
Only return the question.
"""
        try:
            q = hf_generate(prompt, max_tokens=64)
            if not q.endswith("?"):
                q += "?"
            questions.append(q)
        except Exception:
            continue

    return questions

# -------------------------------------------------
# LONG ANSWER QUESTIONS + ANSWERS
# -------------------------------------------------
def generate_long_answers(text, num_questions=3):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 60]
    random.shuffle(sentences)

    qa_pairs = []

    for sent in sentences[:num_questions]:
        q_prompt = f"""
Generate ONE descriptive exam-style question from the content below.
Content: "{sent}"
Only return the question.
"""
        a_prompt = f"""
Answer the following question in at least 5 sentences.
Question: "{sent}"
"""

        try:
            question = hf_generate(q_prompt, max_tokens=80)
            answer = hf_generate(a_prompt, max_tokens=250)
            if not question.endswith("?"):
                question += "?"
            qa_pairs.append((question, answer))
        except Exception:
            continue

    return qa_pairs

# -------------------------------------------------
# FLASHCARDS
# -------------------------------------------------
def generate_flashcards(text, num_cards=5):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 40]
    random.shuffle(sentences)

    cards = []

    for sent in sentences[:num_cards]:
        q_prompt = f"""
Create a flashcard question from the content below.
Content: "{sent}"
Only return the question.
"""
        a_prompt = f"""
Give a clear, short answer for the following concept:
"{sent}"
"""

        try:
            q = hf_generate(q_prompt, max_tokens=60)
            a = hf_generate(a_prompt, max_tokens=120)
            cards.append((q, a))
        except Exception:
            continue

    return cards

# -------------------------------------------------
# REVISION NOTES
# -------------------------------------------------
def generate_revision_notes(text, num_points=5):
    prompt = f"""
Create {num_points} concise revision bullet points from the content below.
Content:
{text}
"""

    try:
        output = hf_generate(prompt, max_tokens=300)
        notes = [line.strip("•- ") for line in output.split("\n") if line.strip()]
        return notes
    except Exception:
        return []
