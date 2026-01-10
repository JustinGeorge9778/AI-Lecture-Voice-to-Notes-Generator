import streamlit as st
import tempfile

from speech_to_text import transcribe_audio_with_timestamps
from quiz_generator import (
    generate_quiz,
    generate_flashcards,
    generate_long_qa,
    generate_mcqs,
    generate_revision_notes
)
from lecture_chatbot import lecture_chatbot_answer
from concept_extractor import extract_concepts

# ================= CONFIG =================
st.set_page_config(page_title="Lecture Voice-to-Notes", layout="wide")

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "history" not in st.session_state:
    st.session_state.history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# 🔥 IMPORTANT: store MCQs once
if "mcqs" not in st.session_state:
    st.session_state.mcqs = None

# ================= SIDEBAR =================
difficulty = st.sidebar.selectbox("🎯 Difficulty Level", ["Easy", "Medium", "Hard"])

# ================= HELPERS =================
def load_audio():
    audio = st.file_uploader("Upload Lecture Audio", type=["wav", "mp3"])
    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio.read())
            return f.name
    return None

def get_transcript(path):
    chunks = transcribe_audio_with_timestamps(path)
    return " ".join(c["text"] for c in chunks)

def save_history(section):
    st.session_state.history.append(section)

# ================= HOME =================
if st.session_state.page == "home":
    st.markdown(
        "<h1 style='text-align:center;'>🎓 AI Lecture Voice-to-Notes Generator</h1>"
        "<p style='text-align:center;'>AI-powered learning from lecture audio</p>",
        unsafe_allow_html=True
    )

    path = load_audio()

    if path and st.session_state.transcript is None:
        with st.spinner("Transcribing lecture..."):
            st.session_state.transcript = get_transcript(path)
            st.session_state.mcqs = None  # reset MCQs on new audio
            st.success("✅ Lecture transcribed successfully!")

    if st.session_state.transcript:
        st.info("👉 Choose an option below to continue.")

    disabled = st.session_state.transcript is None

    c1, c2, c3 = st.columns(3)

    with c1:
        if st.button("❓ Quiz Questions", disabled=disabled):
            st.session_state.page = "quiz"
        if st.button("📝 MCQs", disabled=disabled):
            st.session_state.page = "mcq"

    with c2:
        if st.button("🧠 Flashcards", disabled=disabled):
            st.session_state.page = "flashcards"
        if st.button("📖 Long Answer Q&A", disabled=disabled):
            st.session_state.page = "long"

    with c3:
        if st.button("📌 Revision Notes", disabled=disabled):
            st.session_state.page = "revision"
        if st.button("💬 Lecture Chatbot", disabled=disabled):
            st.session_state.page = "chatbot"

# ================= MCQs (FINAL FIX) =================
elif st.session_state.page == "mcq":
    st.subheader("📝 Multiple Choice Questions")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    # 🔥 Generate MCQs ONLY ONCE
    if st.session_state.mcqs is None:
        st.session_state.mcqs = generate_mcqs(
            st.session_state.transcript, difficulty
        )

    mcqs = st.session_state.mcqs

    with st.form("mcq_form"):
        user_answers = {}

        for i, mcq in enumerate(mcqs, 1):
            st.markdown(f"### Q{i}. {mcq['question']}")

            choice = st.radio(
                "Choose one:",
                ["Select an option"] + list(mcq["options"].keys()),
                format_func=lambda x: (
                    x if x == "Select an option"
                    else f"{x}. {mcq['options'][x]}"
                ),
                index=0,
                key=f"mcq_{i}"
            )

            user_answers[i] = choice

        submitted = st.form_submit_button("✅ Submit Answers")

    if submitted:
        score = 0
        for i, mcq in enumerate(mcqs, 1):
            selected = user_answers[i]
            correct = mcq["answer"]

            if selected != "Select an option" and selected == correct:
                score += 1
                st.success(f"Q{i}: ✔ Correct")
            else:
                st.error(f"Q{i}: ✘ Correct answer is {correct}")

        st.success(f"🎯 Final Score: {score} / {len(mcqs)}")
        save_history("MCQs")

# ================= OTHER PAGES (UNCHANGED) =================
elif st.session_state.page == "quiz":
    st.subheader("❓ Quiz Questions")
    if st.button("⬅ Back"):
        st.session_state.page = "home"
    for i, q in enumerate(generate_quiz(st.session_state.transcript, difficulty), 1):
        st.write(f"{i}. {q}")

elif st.session_state.page == "flashcards":
    st.subheader("🧠 Flashcards")
    if st.button("⬅ Back"):
        st.session_state.page = "home"
    for i, (q, a) in enumerate(generate_flashcards(st.session_state.transcript), 1):
        with st.expander(f"Flashcard {i}"):
            st.write("**Q:**", q)
            st.write("**A:**", a)

elif st.session_state.page == "long":
    st.subheader("📖 Long Answer Q&A")
    if st.button("⬅ Back"):
        st.session_state.page = "home"
    for i, (q, a) in enumerate(generate_long_qa(st.session_state.transcript, difficulty), 1):
        with st.expander(f"Question {i}"):
            st.write(q)
            st.write(a)

elif st.session_state.page == "revision":
    st.subheader("📌 Revision Notes")
    if st.button("⬅ Back"):
        st.session_state.page = "home"
    concepts = extract_concepts(st.session_state.transcript)
    for note in generate_revision_notes(concepts, difficulty):
        st.write(note)

elif st.session_state.page == "chatbot":
    st.subheader("💬 Lecture Chatbot")
    if st.button("⬅ Back"):
        st.session_state.page = "home"

    q = st.text_input("Ask a question:")
    if st.button("Ask") and q.strip():
        a = lecture_chatbot_answer(st.session_state.transcript, q)
        st.write(a)
