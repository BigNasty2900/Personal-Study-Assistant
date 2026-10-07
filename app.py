import streamlit as st
import os
import json
import random
from openai import OpenAI

# --------------------------------------------------
# SETUP
# --------------------------------------------------

api_key = os.getenv("OPENAI_API_KEY")

# Support Streamlit Cloud secrets
if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass

st.set_page_config(
    page_title="Personal Study Assistant",
    page_icon="📚",
    layout="wide"
)

if not api_key:
    st.error("API key not found.")
    st.stop()

client = OpenAI(api_key=api_key)


# --------------------------------------------------
# FILE HELPERS
# --------------------------------------------------

def load_json(filename, default):
    if os.path.exists(filename):
        try:
            with open(filename, "r") as file:
                return json.load(file)
        except:
            return default
    return default


def save_json(filename, data):
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


# --------------------------------------------------
# LOAD SAVED DATA
# --------------------------------------------------

if "notes" not in st.session_state:
    st.session_state.notes = load_json("notes.json", [])

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = load_json(
        "conversation_history.json", []
    )

if "study_history" not in st.session_state:
    st.session_state.study_history = load_json(
        "study_history.json", []
    )


# --------------------------------------------------
# AI HELPER
# --------------------------------------------------

def ask_ai(prompt):
    response = client.responses.create(
        model="gpt-6-luna",
        input=prompt
    )

    return response.output_text


# --------------------------------------------------
# TITLE
# --------------------------------------------------

st.title("📚 Personal Study Assistant")
st.write("Your AI-powered study companion.")

st.divider()


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

st.sidebar.title("Study Tools")

page = st.sidebar.radio(
    "Choose a feature:",
    [
        "🤖 Ask AI",
        "📝 Quiz Mode",
        "📓 Notes",
        "💬 Conversation History",
        "📚 Study Mode",
        "📊 Study History"
    ]
)


# ==================================================
# ASK AI
# ==================================================

if page == "🤖 Ask AI":

    st.header("🤖 Ask AI")

    question = st.text_area(
        "What would you like to learn about?",
        placeholder="Example: Explain Python loops in simple terms."
    )

    if st.button("Ask AI", type="primary"):

        if question.strip():

            with st.spinner("Thinking..."):

                response = ask_ai(
                    f"""
You are a helpful personal study assistant.

Answer the student's question clearly and simply.

Question:
{question}
"""
                )

            st.subheader("Answer")
            st.write(response)

            st.session_state.conversation_history.append({
                "question": question,
                "response": response
            })

            save_json(
                "conversation_history.json",
                st.session_state.conversation_history
            )

        else:
            st.warning("Please enter a question.")


# ==================================================
# QUIZ MODE
# ==================================================

elif page == "📝 Quiz Mode":

    st.header("📝 Quiz Mode")

    topic = st.text_input(
        "What topic would you like to be quizzed on?"
    )

    difficulty = st.selectbox(
        "Choose difficulty:",
        ["Easy", "Medium", "Hard"]
    )

    if st.button("Generate Quiz Question", type="primary"):

        if topic.strip():

            with st.spinner("Creating your question..."):

                quiz = ask_ai(
                    f"""
Create ONE multiple-choice quiz question about:

{topic}

Difficulty:
{difficulty}

Choose four possible answers.

Randomize the correct answer position.

Return EXACTLY this format:

QUESTION: your question

A: answer
B: answer
C: answer
D: answer

CORRECT: A

EXPLANATION: short explanation

Do not add anything else.
"""
                )

            st.session_state.quiz = quiz

        else:
            st.warning("Please enter a topic.")

    if "quiz" in st.session_state:

        quiz_text = st.session_state.quiz

        lines = quiz_text.splitlines()

        question_text = ""
        choices = []
        correct_answer = ""
        explanation = ""

        for line in lines:

            if line.startswith("QUESTION:"):
                question_text = line.replace(
                    "QUESTION:", ""
                ).strip()

            elif line.startswith(("A:", "B:", "C:", "D:")):
                choices.append(line)

            elif line.startswith("CORRECT:"):
                correct_answer = line.replace(
                    "CORRECT:", ""
                ).strip()

            elif line.startswith("EXPLANATION:"):
                explanation = line.replace(
                    "EXPLANATION:", ""
                ).strip()

        if question_text:

            st.subheader(question_text)

            if choices:

                answer = st.radio(
                    "Choose your answer:",
                    choices,
                    key="quiz_choice"
                )

                if st.button("Check Answer"):

                    selected_letter = answer[0]

                    if selected_letter == correct_answer:
                        st.success("✅ Correct!")

                    else:
                        st.error(
                            f"❌ Incorrect. The correct answer is {correct_answer}."
                        )

                    st.info(
                        f"Explanation: {explanation}"
                    )


# ==================================================
# NOTES
# ==================================================

elif page == "📓 Notes":

    st.header("📓 Notes")

    note_title = st.text_input("Note title")

    note_content = st.text_area(
        "Write your note:"
    )

    if st.button("Save Note", type="primary"):

        if note_title.strip() and note_content.strip():

            new_note = {
                "title": note_title,
                "content": note_content
            }

            st.session_state.notes.append(new_note)

            save_json(
                "notes.json",
                st.session_state.notes
            )

            st.success("Note saved!")

        else:
            st.warning(
                "Please enter both a title and note."
            )

    st.divider()

    st.subheader("Your Notes")

    if len(st.session_state.notes) == 0:

        st.info("You don't have any notes yet.")

    else:

        for index, note in enumerate(
            st.session_state.notes
        ):

            if isinstance(note, dict):
                title = note.get("title", f"Note {index + 1}")
                content = note.get("content", "")
            else:
                title = f"Note {index + 1}"
                content = note

        with st.expander(title):
            st.write(content)

            if st.button(
                "Delete Note",
                key=f"delete_{index}"
            ):
                st.session_state.notes.pop(index)

                save_json(
                    "notes.json",
                    st.session_state.notes
                )

                st.rerun()

# ==================================================
# CONVERSATION HISTORY
# ==================================================

elif page == "💬 Conversation History":

    st.header("💬 Conversation History")

    history = st.session_state.conversation_history

    if len(history) == 0:

        st.info(
            "No conversation history yet."
        )

    else:

        for index, conversation in enumerate(reversed(history), start=1):

            if isinstance(conversation, dict):
                question = conversation.get("question", "")
                answer = conversation.get("response", "")

            elif isinstance(conversation, (list, tuple)):
                question = conversation[0]
                answer = conversation[1]

            else:
                question = "Previous conversation"
                answer = conversation

            st.subheader(f"Conversation {index}")

            st.write(f"**Question:** {question}")
            st.write(f"**Answer:** {answer}")

            st.divider()


# ==================================================
# STUDY MODE
# ==================================================

elif page == "📚 Study Mode":

    st.header("📚 Study Mode")

    st.write(
        "Learn a topic, answer three practice questions, "
        "and receive a score."
    )

    topic = st.text_input(
        "What would you like to study?",
        key="study_topic"
    )

    if st.button(
        "Start Study Session",
        type="primary"
    ):

        if topic.strip():

            with st.spinner(
                "Creating your study lesson..."
            ):

                lesson = ask_ai(
                    f"""
Teach me about {topic}.

Give me:

1. A short lesson
2. Important points to remember

Keep the lesson easy to understand.
Do not create practice questions yet.
"""
                )

            st.session_state.study_topic_active = topic
            st.session_state.study_lesson = lesson
            st.session_state.study_question_number = 1
            st.session_state.study_score = 0
            st.session_state.study_finished = False
            st.session_state.study_current_question = None
            st.session_state.study_checked = False

        else:
            st.warning("Please enter a topic.")

    # ----------------------------------------------
    # SHOW LESSON
    # ----------------------------------------------

    if "study_lesson" in st.session_state:

        st.subheader(
            f"Lesson: {st.session_state.study_topic_active}"
        )

        st.write(
            st.session_state.study_lesson
        )

        st.divider()

        # ------------------------------------------
        # FINISHED
        # ------------------------------------------

        if st.session_state.get(
            "study_finished",
            False
        ):

            score = st.session_state.study_score

            st.subheader("🎯 Study Session Complete")

            st.metric(
                "Final Score",
                f"{score}/3"
            )

            if score == 3:
                st.success(
                    "Excellent! You really understand this topic."
                )
            elif score == 2:
                st.success(
                    "Good job! You understand most of the topic."
                )
            elif score == 1:
                st.warning(
                    "Keep practicing. You're making progress."
                )
            else:
                st.error(
                    "Review the topic and try again."
                )

            if st.button("Try This Topic Again"):

                st.session_state.study_question_number = 1
                st.session_state.study_score = 0
                st.session_state.study_finished = False
                st.session_state.study_current_question = None
                st.session_state.study_checked = False

                st.rerun()

        else:

            # --------------------------------------
            # GENERATE QUESTION
            # --------------------------------------

            if st.session_state.get(
                "study_current_question"
            ) is None:

                number = st.session_state.study_question_number

                with st.spinner(
                    "Creating practice question..."
                ):

                    question = ask_ai(
                        f"""
Create ONE practice question about:

{st.session_state.study_topic_active}

This is practice question {number} of 3.

Give ONLY the question.
Do not give the answer.
"""
                    )

                st.session_state.study_current_question = question
                st.session_state.study_checked = False

            # --------------------------------------
            # SHOW QUESTION
            # --------------------------------------

            st.subheader(
                f"Practice Question "
                f"{st.session_state.study_question_number}/3"
            )

            st.write(
                st.session_state.study_current_question
            )

            user_answer = st.text_area(
                "Your answer:",
                key=f"study_answer_{st.session_state.study_question_number}"
            )

            if not st.session_state.study_checked:

                if st.button("Check My Answer"):

                    if user_answer.strip():

                        with st.spinner(
                            "Checking your answer..."
                        ):

                            feedback = ask_ai(
                                f"""
Topic:
{st.session_state.study_topic_active}

Question:
{st.session_state.study_current_question}

Student's answer:
{user_answer}

Check the student's answer.

Your response MUST start with exactly:

CORRECT

or

INCORRECT

Then briefly explain why.
"""
                            )

                        st.session_state.study_feedback = feedback
                        st.session_state.study_checked = True

                        if feedback.strip().upper().startswith(
                            "CORRECT"
                        ):
                            st.session_state.study_score += 1

                        st.rerun()

                    else:
                        st.warning(
                            "Please enter an answer."
                        )

            # --------------------------------------
            # SHOW FEEDBACK
            # --------------------------------------

            if st.session_state.get(
                "study_checked",
                False
            ):

                feedback = st.session_state.study_feedback

                if feedback.upper().startswith("CORRECT"):

                    st.success(feedback)

                else:

                    st.error(feedback)

                if st.session_state.study_question_number < 3:

                    if st.button("Next Question"):

                        st.session_state.study_question_number += 1
                        st.session_state.study_current_question = None
                        st.session_state.study_checked = False

                        st.rerun()

                else:

                    if st.button(
                        "Finish Study Session",
                        type="primary"
                    ):

                        score = st.session_state.study_score

                        st.session_state.study_finished = True

                        st.session_state.study_history.append({
                            "topic": st.session_state.study_topic_active,
                            "score": score
                        })

                        save_json(
                            "study_history.json",
                            st.session_state.study_history
                        )

                        st.rerun()


# ==================================================
# STUDY HISTORY
# ==================================================

elif page == "📊 Study History":

    st.header("📊 Study History")

    history = st.session_state.study_history

    if len(history) == 0:

        st.info(
            "No study sessions yet."
        )

    else:

        total_score = sum(
            session["score"]
            for session in history
        )

        total_questions = len(history) * 3

        average = (
            total_score / total_questions * 100
        )

        st.metric(
            "Average Score",
            f"{average:.0f}%"
        )

        st.divider()

        for session in reversed(history):

            st.write(
                f"📚 **{session['topic']}** — "
                f"{session['score']}/3"
            )