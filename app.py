import streamlit as st
import os
import io
import re
import random
import copy

# Import libraries with error handling
try:
    import pdfplumber
except ImportError:
    pdfplumber = None

try:
    from docx import Document
except ImportError:
    Document = None

# ---------- Constants ----------
MAX_UPLOAD_MB = 5
MAX_UPLOAD_BYTES = MAX_UPLOAD_MB * 1024 * 1024

# Streamlit page config
st.set_page_config(
    page_title="AI Quiz Generator",
    page_icon="📚",
    layout="wide"
)

# ---------- Helpers ----------
def check_platform_compatibility():
    import platform
    with st.sidebar:
        st.info(f"🖥️ Running on: {platform.system()}")
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if api_key:
            st.success("🔑 API Key configured")
        else:
            st.warning("🔑 No API Key - Using local generation")
    return True

def apply_custom_styling():
    st.markdown("""
    <style>
    .stApp {font-family: 'Nunito Sans', sans-serif;}
    </style>
    """, unsafe_allow_html=True)

def fix_file_uploader_limit_label(file_types="PDF"):
    """Override Streamlit's default 200MB text to show 5MB"""
    st.markdown(
        f"""
        <style>
        .stFileUploader div[data-testid="stFileUploaderDropzone"] small {{
            visibility: hidden;
            position: relative;
        }}
        .stFileUploader div[data-testid="stFileUploaderDropzone"] small:after {{
            content: "Limit {MAX_UPLOAD_MB}MB per file • {file_types}";
            visibility: visible;
            position: absolute;
            left: 0;
            top: 0;
            color: #bbb;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def _enforce_size(uploaded_file, label="file"):
    try:
        size = getattr(uploaded_file, "size", None)
        if size is None:
            uploaded_file.seek(0, os.SEEK_END)
            size = uploaded_file.tell()
            uploaded_file.seek(0)
        if size > MAX_UPLOAD_BYTES:
            st.error(f"❌ {label} is too large. Max allowed is {MAX_UPLOAD_MB} MB.")
            return False
        return True
    except Exception:
        st.error("❌ Could not validate file size. Please re-upload a smaller file.")
        return False

def extract_text_from_pdf(pdf_file):
    if pdfplumber is None:
        raise Exception("pdfplumber is required for PDF processing.")
    text_content = []
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                text_content.append(text)
    extracted_text = "\n\n".join(text_content)
    if not extracted_text.strip():
        raise Exception("No text extracted. File may be image-only or protected.")
    return extracted_text

def extract_text_from_article(article_text):
    if not article_text.strip():
        raise Exception("Article text cannot be empty.")
    cleaned = re.sub(r'\n\s*\n', '\n\n', article_text.strip())
    cleaned = re.sub(r' +', ' ', cleaned)
    if len(cleaned) < 100:
        raise Exception("Article text too short (min 100 chars).")
    return cleaned

def generate_questions_with_gemini_ai(text_content, num_mc=5, num_tf=5, difficulty="medium"):
    try:
        from gemini_quiz_generator import GeminiQuizGenerator
        generator = GeminiQuizGenerator()
        return generator.generate_quiz(text_content, difficulty, num_mc, num_tf)
    except Exception:
        return create_intelligent_questions(text_content, num_mc, num_tf, difficulty)

def create_intelligent_questions(content, num_mc=5, num_tf=5, difficulty="medium", question_types=["multiple_choice","true_false"]):
    sentences = [s.strip() for s in re.split(r'[.!?]+', content) if len(s.strip()) > 20]
    words = content.split()
    common_words = {'the','and','for','are','but','not','you','all','can','had','her','was','one','our','out','day','get','has'}
    key_terms = [w for w in words if len(w) > 4 and w.lower() not in common_words][:15]

    multiple_choice, true_false = [], []
    if "multiple_choice" in question_types and key_terms:
        for i, term in enumerate(key_terms[:num_mc]):
            question = f"What is {term}?"
            options = ["Correct meaning", "Not mentioned", "Unrelated", "Minor detail"]
            random.shuffle(options)
            multiple_choice.append({
                "question": question,
                "options": [f"{chr(65+j)}) {opt}" for j, opt in enumerate(options)],
                "correct_answer": "A",
                "explanation": f"{term} is key in the text."
            })
    if "true_false" in question_types and sentences:
        for i, s in enumerate(sentences[:num_tf]):
            true_false.append({
                "question": s[:120],
                "correct_answer": "True",
                "explanation": "From the content."
            })
    return {"multiple_choice": multiple_choice, "true_false": true_false}

def export_quiz_txt(data):
    content = "QUIZ QUESTIONS\n" + "="*50 + "\n\n"
    for i, q in enumerate(data.get("multiple_choice", [])):
        content += f"{i+1}. {q['question']}\n"
        for opt in q['options']:
            content += f"   {opt}\n"
        content += f"   Answer: {q['correct_answer']}\n"
        content += f"   Explanation: {q['explanation']}\n\n"
    for i, q in enumerate(data.get("true_false", [])):
        content += f"{len(data.get('multiple_choice', []))+i+1}. {q['question']}\n"
        content += f"   Answer: {q['correct_answer']}\n"
        content += f"   Explanation: {q['explanation']}\n\n"
    return content.encode("utf-8")

def export_quiz_docx(data):
    if Document is None: raise Exception("python-docx not installed")
    doc = Document()
    doc.add_heading("Quiz Questions", 0)
    for i, q in enumerate(data.get("multiple_choice", [])):
        doc.add_paragraph(f"{i+1}. {q['question']}")
        for opt in q['options']: doc.add_paragraph(opt, style="List Bullet")
        doc.add_paragraph(f"Answer: {q['correct_answer']}")
        doc.add_paragraph(f"Explanation: {q['explanation']}")
    for i, q in enumerate(data.get("true_false", [])):
        doc.add_paragraph(f"{len(data.get('multiple_choice', []))+i+1}. {q['question']}")
        doc.add_paragraph(f"Answer: {q['correct_answer']}")
        doc.add_paragraph(f"Explanation: {q['explanation']}")
    buf = io.BytesIO()
    doc.save(buf)
    buf.seek(0)
    return buf.getvalue()

# ---------- Main ----------
def main():
    check_platform_compatibility()
    apply_custom_styling()

    st.title("📚 AI Quiz Generator")

    with st.sidebar:
        st.header("⚙️ Settings")
        difficulty = st.radio("Difficulty", ["easy","medium","hard"], index=1)
        include_mc = st.checkbox("Multiple Choice", True)
        include_tf = st.checkbox("True/False", True)
        num_mc = st.slider("MCQs", 1, 10, 5) if include_mc else 0
        num_tf = st.slider("T/F", 1, 10, 5) if include_tf else 0
        if not include_mc and not include_tf: st.stop()

    st.subheader("Upload PDF (≤5 MB)")
    uploaded_file = st.file_uploader("Choose a PDF file:", type=["pdf"])
    fix_file_uploader_limit_label("PDF")

    extracted_text = None
    if uploaded_file:
        if _enforce_size(uploaded_file, "PDF"):
            extracted_text = extract_text_from_pdf(uploaded_file)

    article_text = st.text_area("Or paste article text (min 100 chars)")
    if article_text:
        extracted_text = extract_text_from_article(article_text)

    if extracted_text and st.button("Generate Quiz"):
        qdata = generate_questions_with_gemini_ai(extracted_text, num_mc, num_tf, difficulty)
        st.session_state.quiz = copy.deepcopy(qdata)
        st.success("✅ Quiz Generated!")

    if "quiz" in st.session_state:
        st.subheader("📥 Export Quiz")
        col1, col2 = st.columns(2)
        with col1:
            st.download_button("Download TXT", export_quiz_txt(st.session_state.quiz), "quiz.txt", "text/plain")
        with col2:
            st.download_button("Download DOCX", export_quiz_docx(st.session_state.quiz), "quiz.docx",
                               "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

if __name__ == "__main__":
    main()
