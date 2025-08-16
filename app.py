import streamlit as st
import os
import json
import random
import copy
from io import BytesIO

# Document handling
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from docx import Document

# Custom modules (make sure these files exist in your project)
from file_processor import FileProcessor
from gemini_quiz_generator import GeminiQuizGenerator


# -------------------------------
# PDF Export Utility
# -------------------------------
def export_pdf(questions, filename="quiz.pdf"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []

    for i, q in enumerate(questions, start=1):
        story.append(Paragraph(f"Q{i}: {q['question']}", styles['Normal']))
        for option in q['options']:
            story.append(Paragraph(f"- {option}", styles['Normal']))
        story.append(Spacer(1, 12))

    doc.build(story)
    buffer.seek(0)
    return buffer


# -------------------------------
# Local Quiz Generator (fallback)
# -------------------------------
def generate_quiz_locally(content, num_questions=5):
    sample_questions = [
        {
            "question": "What is the capital of France?",
            "options": ["Paris", "London", "Berlin", "Madrid"],
            "answer": "Paris",
        },
        {
            "question": "Which programming language is known as the backbone of web development?",
            "options": ["Python", "JavaScript", "C++", "Java"],
            "answer": "JavaScript",
        },
        {
            "question": "Who developed the theory of relativity?",
            "options": ["Newton", "Einstein", "Tesla", "Edison"],
            "answer": "Einstein",
        },
        {
            "question": "Which planet is known as the Red Planet?",
            "options": ["Earth", "Mars", "Jupiter", "Venus"],
            "answer": "Mars",
        },
        {
            "question": "What is the chemical symbol for water?",
            "options": ["O2", "H2O", "CO2", "NaCl"],
            "answer": "H2O",
        },
    ]
    return random.sample(sample_questions, min(num_questions, len(sample_questions)))


# -------------------------------
# Export as TXT or DOCX
# -------------------------------
def export_quiz(questions, file_format="txt"):
    if file_format == "txt":
        output = "\n".join(
            f"Q{i+1}: {q['question']}\nOptions: {', '.join(q['options'])}\nAnswer: {q['answer']}\n"
            for i, q in enumerate(questions)
        )
        return output

    elif file_format == "docx":
        doc = Document()
        doc.add_heading("Quiz", 0)
        for i, q in enumerate(questions, start=1):
            doc.add_paragraph(f"Q{i}: {q['question']}")
            for option in q['options']:
                doc.add_paragraph(f"- {option}", style="List Bullet")
            doc.add_paragraph(f"Answer: {q['answer']}")
            doc.add_paragraph("\n")
        buffer = BytesIO()
        doc.save(buffer)
        buffer.seek(0)
        return buffer


# -------------------------------
# Custom CSS
# -------------------------------
def local_css():
    st.markdown(
        """
        <style>
        .title {font-size:36px !important; color:#1E90FF; text-align:center; font-weight:bold;}
        .subtitle {font-size:20px !important; color:#4682B4; text-align:center;}
        .stButton>button {background-color:#1E90FF; color:white; border-radius:12px; padding:10px 20px;}
        .stDownloadButton>button {background-color:#32CD32; color:white; border-radius:12px; padding:10px 20px;}
        </style>
        """,
        unsafe_allow_html=True,
    )


# -------------------------------
# Main App
# -------------------------------
def main():
    st.set_page_config(page_title="AI Quiz Generator", layout="centered")
    local_css()

    st.markdown('<p class="title">AI Quiz Generator</p>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Generate quizzes from text, PDFs, CSVs, or articles</p>', unsafe_allow_html=True)

    file_processor = FileProcessor()
    api_key = os.getenv("GEMINI_API_KEY")
    gemini_quiz_generator = GeminiQuizGenerator(api_key) if api_key else None

    uploaded_file = st.file_uploader("Upload File (PDF, TXT, CSV)", type=["pdf", "txt", "csv"])
    article_url = st.text_input("Or paste an article URL")
    manual_input = st.text_area("Or paste your own content here")

    num_questions = st.number_input("Number of Questions", min_value=1, max_value=20, value=5)

    # Store generated questions in session
    if "edited_questions" not in st.session_state:
        st.session_state.edited_questions = []

    # -------------------------------
    # Generate Quiz
    # -------------------------------
    if st.button("Generate Quiz"):
        content = ""

        if uploaded_file:
            # Check file size (limit 5 MB = 5 * 1024 * 1024 bytes)
            if uploaded_file.size > 5 * 1024 * 1024:
                st.error("❌ File size exceeds 5 MB limit.")
                return
            file_type = uploaded_file.type
            if file_type == "application/pdf":
                content = file_processor.process_pdf(uploaded_file)
            elif file_type == "text/plain":
                content = file_processor.process_txt(uploaded_file)
            elif file_type == "text/csv":
                content = file_processor.process_csv(uploaded_file)
        elif article_url:
            content = file_processor.process_url(article_url)
        elif manual_input:
            content = manual_input

        if not content:
            st.error("Please upload a file, paste a URL, or provide text.")
            return

        try:
            if gemini_quiz_generator:
                questions_data = gemini_quiz_generator.generate_quiz(content, num_questions)
            else:
                questions_data = generate_quiz_locally(content, num_questions)

            st.session_state.edited_questions = copy.deepcopy(questions_data)
            st.success("✅ Quiz generated successfully!")
        except Exception as e:
            st.error(f"Error generating quiz: {e}")

    # -------------------------------
    # Display Quiz Editor
    # -------------------------------
    if st.session_state.edited_questions:
        st.subheader("📝 Edit Quiz Questions")

        for i, q in enumerate(st.session_state.edited_questions):
            st.session_state.edited_questions[i]["question"] = st.text_input(
                f"Q{i+1}", q["question"], key=f"q_{i}"
            )
            options = []
            for j, option in enumerate(q["options"]):
                options.append(st.text_input(f"Option {j+1} for Q{i+1}", option, key=f"opt_{i}_{j}"))
            st.session_state.edited_questions[i]["options"] = options
            st.session_state.edited_questions[i]["answer"] = st.text_input(
                f"Answer for Q{i+1}", q["answer"], key=f"ans_{i}"
            )

        # -------------------------------
        # Download Options
        # -------------------------------
        st.subheader("📥 Download Quiz")

        col1, col2, col3 = st.columns(3)

        with col1:
            txt_data = export_quiz(st.session_state.edited_questions, "txt")
            st.download_button(
                label="📄 Download as TXT",
                data=txt_data,
                file_name="quiz_questions.txt",
                mime="text/plain"
            )

        with col2:
            docx_data = export_quiz(st.session_state.edited_questions, "docx")
            st.download_button(
                label="📑 Download as DOCX",
                data=docx_data,
                file_name="quiz_questions.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

        with col3:
            pdf_buffer = export_pdf(st.session_state.edited_questions)
            st.download_button(
                label="📘 Download as PDF",
                data=pdf_buffer,
                file_name="quiz_questions.pdf",
                mime="application/pdf"
            )


if __name__ == "__main__":
    main()
