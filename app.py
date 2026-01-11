import streamlit as st
import tempfile

from speech_to_text import transcribe_audio_with_timestamps
from quiz_generator import (
    generate_quiz,
    generate_flashcards,
    generate_long_qa,
    generate_mcqs
)
from lecture_chatbot import lecture_chatbot_answer

# ================= CONFIG =================
st.set_page_config(
    page_title="AI Lecture Voice-to-Notes Generator",
    layout="wide"
)

# ================= SESSION STATE =================
if "page" not in st.session_state:
    st.session_state.page = "home"

if "history" not in st.session_state:
    st.session_state.history = []

if "transcript" not in st.session_state:
    st.session_state.transcript = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mcqs" not in st.session_state:
    st.session_state.mcqs = None

# ================= SIDEBAR =================
difficulty = st.sidebar.selectbox(
    "🎯 Difficulty Level",
    ["Easy", "Medium", "Hard"]
)

# ================= HELPERS =================
def load_audio():
    audio = st.file_uploader(
        "Upload Lecture Audio",
        type=["wav", "mp3"]
    )
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
            st.session_state.mcqs = None
            st.success("✅ Lecture transcribed successfully!")

    if st.session_state.transcript:
        st.info("👉 Choose an option below to generate study materials.")

        with st.expander("📄 View Transcribed Lecture"):
            st.write(st.session_state.transcript[:1500] + " ...")

    disabled = st.session_state.transcript is None

    st.markdown("---")

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
        if st.button("💬 Lecture Chatbot", disabled=disabled):
            st.session_state.page = "chatbot"

# ================= MCQs =================
elif st.session_state.page == "mcq":
    st.subheader("📝 Multiple Choice Questions")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

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

# ================= QUIZ =================
elif st.session_state.page == "quiz":
    st.subheader("❓ Quiz Questions")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    questions = generate_quiz(
        st.session_state.transcript, difficulty
    )

    for i, q in enumerate(questions, 1):
        st.write(f"{i}. {q}")

    save_history("Quiz")

# ================= FLASHCARDS =================
elif st.session_state.page == "flashcards":
    st.subheader("🧠 Flashcards")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    cards = generate_flashcards(st.session_state.transcript)

    for i, (q, a) in enumerate(cards, 1):
        with st.expander(f"Flashcard {i}"):
            st.write("**Q:**", q)
            st.write("**A:**", a)

    save_history("Flashcards")

# ================= LONG ANSWERS =================
elif st.session_state.page == "long":
    st.subheader("📖 Long Answer Questions")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    qa_pairs = generate_long_qa(
        st.session_state.transcript, difficulty
    )

    for i, (q, a) in enumerate(qa_pairs, 1):
        with st.expander(f"Question {i}"):
            st.write("**Question:**")
            st.write(q)
            st.write("**Answer:**")
            st.write(a)

    save_history("Long Answers")

# ================= CHATBOT =================
elif st.session_state.page == "chatbot":
    st.subheader("💬 Lecture Chatbot")

    if st.button("⬅ Back"):
        st.session_state.page = "home"

    question = st.text_input(
        "Ask a question from the lecture:",
        placeholder="Explain the main concept in simple terms"
    )

    if st.button("Ask"):
        if question.strip():
            with st.spinner("Thinking..."):
                answer = lecture_chatbot_answer(
                    st.session_state.transcript,
                    question
                )
            st.session_state.chat_history.append((question, answer))

    if st.button("🗑 Clear Chat"):
        st.session_state.chat_history = []

    for q, a in reversed(st.session_state.chat_history):
        st.markdown(f"**🧑 You:** {q}")
        st.markdown(f"**🤖 AI:** {a}")
        st.markdown("---")
