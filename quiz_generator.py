from transformers import pipeline
import nltk
import re
import random
from nltk.tokenize import sent_tokenize

nltk.download("punkt")

# Hugging Face model
qg = pipeline("text2text-generation", model="google/flan-t5-base")

# ---------------- Utility ----------------
def get_sentences(text, limit=5):
    sentences = sent_tokenize(text)
    return [s for s in sentences if len(s.split()) > 6][:limit]

def clean_question(text):
    text = re.split(r"Options:|Answer:", text)[0]
    if "?" in text:
        text = text.split("?")[0] + "?"
    return text.strip()

# ---------------- QUIZ QUESTIONS ----------------
def generate_quiz(text, difficulty="Medium"):
    questions = []
    sentences = get_sentences(text)

    for s in sentences:
        prompt = (
            f"Generate a {difficulty.lower()} WHY or HOW question.\n"
            "Do NOT ask WHAT questions.\n\n"
            f"Sentence:\n{s}"
        )

        q = qg(
            prompt,
            max_length=80,
            do_sample=True,
            temperature=0.9
        )[0]["generated_text"]

        q = clean_question(q)
        if q and q not in questions:
            questions.append(q)

    return questions

# ---------------- FLASHCARDS ----------------
def generate_flashcards(text):
    cards = []
    sentences = get_sentences(text)

    for s in sentences:
        prompt = (
            "Generate a short WHAT or DEFINE style flashcard question.\n\n"
            f"Sentence:\n{s}"
        )

        q = qg(
            prompt,
            max_length=60,
            do_sample=True,
            temperature=0.6
        )[0]["generated_text"]

        q = clean_question(q)
        cards.append((q, s))

    return cards

# ---------------- LONG ANSWER Q&A ----------------
def generate_long_qa(text, difficulty="Medium", num_pairs=3):
    qa_pairs = []
    sentences = get_sentences(text, num_pairs)

    for s in sentences:
        q_prompt = (
            f"Generate a {difficulty.lower()} long-answer exam question "
            f"based on the idea below:\n\n{s}"
        )

        question = qg(
            q_prompt,
            max_length=90,
            do_sample=True,
            temperature=0.9
        )[0]["generated_text"]

        a_prompt = (
            f"Write a detailed {difficulty.lower()} answer of at least six sentences "
            f"explaining the idea below:\n\n{s}"
        )

        answer = qg(
            a_prompt,
            max_length=400,
            do_sample=True,
            temperature=0.8
        )[0]["generated_text"]

        qa_pairs.append((clean_question(question), answer))

    return qa_pairs

# ---------------- MCQs (FIXED ONLY AS REQUESTED) ----------------
def generate_mcqs(text, difficulty="Medium", num_mcqs=5):
    mcqs = []

    prompt = (
        f"Generate {num_mcqs} {difficulty.lower()} multiple choice questions.\n"
        "FORMAT STRICTLY:\n"
        "QUESTION: <question>\n"
        "A) <option>\n"
        "B) <option>\n"
        "C) <option>\n"
        "D) <option>\n"
        "CORRECT: <A/B/C/D>\n\n"
        f"PASSAGE:\n{text}"
    )

    output = qg(
        prompt,
        max_length=1200,
        do_sample=True,
        temperature=0.9
    )[0]["generated_text"]

    blocks = re.split(r"QUESTION:", output)

    for block in blocks:
        if "CORRECT:" not in block:
            continue

        lines = block.strip().split("\n")
        question = clean_question(lines[0])

        options = {}
        for line in lines:
            if line.startswith(("A)", "B)", "C)", "D)")):
                options[line[0]] = line[2:].strip()

        try:
            original_answer = block.split("CORRECT:")[1].strip()[0]
        except:
            continue

        if len(options) == 4 and original_answer in options:
            # 🔀 SHUFFLE OPTIONS (FIX 1)
            items = list(options.items())
            random.shuffle(items)

            shuffled_options = {}
            new_answer = None

            for idx, (old_key, text) in enumerate(items):
                new_key = chr(65 + idx)
                shuffled_options[new_key] = text
                if old_key == original_answer:
                    new_answer = new_key

            mcqs.append({
                "question": question,
                "options": shuffled_options,
                "answer": new_answer
            })

    # ---------------- FALLBACK (FIXED) ----------------
    if not mcqs:
        sentences = get_sentences(text, num_mcqs)

        for s in sentences:
            options = random.sample(sentences, min(4, len(sentences)))
            while len(options) < 4:
                options.append("None of the above")

            random.shuffle(options)
            correct_index = random.randint(0, 3)

            opts = {chr(65 + i): o for i, o in enumerate(options)}

            mcqs.append({
                "question": clean_question(s),
                "options": opts,
                "answer": chr(65 + correct_index)
            })

    return mcqs[:num_mcqs]

# ---------------- REVISION NOTES ----------------
def generate_revision_notes(concepts, difficulty="Medium"):
    notes = []

    for c in concepts:
        prompt = (
            f"Write {difficulty.lower()} revision notes in bullet points "
            f"for the following concept:\n\n{c}"
        )

        output = qg(
            prompt,
            max_length=120,
            do_sample=True,
            temperature=0.6
        )[0]["generated_text"]

        notes.append(output)

    return notes
