import streamlit as st
import json
import os
import requests
import io
from docx import Document
from docx.shared import Inches

try:
    import pdfplumber
except ImportError:
    pdfplumber = None

# Configure Streamlit page
st.set_page_config(
    page_title="PDF Quiz Generator",
    page_icon="📚",
    layout="wide"
)

def extract_text_from_pdf(pdf_file):
    """
    Extract clean, readable text from uploaded PDF file using pdfplumber
    """
    if pdfplumber is None:
        raise Exception("pdfplumber is required for PDF processing. Please install it.")
    
    try:
        text_content = []
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_content.append(text)
        
        extracted_text = '\n\n'.join(text_content)
        
        if not extracted_text.strip():
            raise Exception("No text could be extracted from the PDF. The PDF might contain only images or be password protected.")
        
        return extracted_text
    
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def extract_text_from_article(article_text):
    """
    Process and clean article text for quiz generation
    """
    if not article_text or not article_text.strip():
        raise Exception("Article text cannot be empty.")
    
    # Basic text cleaning
    cleaned_text = article_text.strip()
    
    # Remove excessive whitespace and normalize line breaks
    import re
    cleaned_text = re.sub(r'\n\s*\n', '\n\n', cleaned_text)
    cleaned_text = re.sub(r' +', ' ', cleaned_text)
    
    if len(cleaned_text) < 100:
        raise Exception("Article text is too short. Please provide at least 100 characters for meaningful quiz generation.")
    
    return cleaned_text

def generate_questions_with_hf(text_content, num_mc=5, num_tf=5):
    """
    Generate quiz questions using Hugging Face Inference API
    """
    hf_token = os.getenv("HUGGINGFACE_API_KEY", "")
    
    if not hf_token:
        raise Exception("HUGGINGFACE_API_KEY environment variable is required")
    
    # Use Google Flan-T5 model for better instruction following
    api_url = "https://api-inference.huggingface.co/models/google/flan-t5-large"
    headers = {"Authorization": f"Bearer {hf_token}"}
    
    # Truncate content to avoid token limits
    content_snippet = text_content[:2000] if len(text_content) > 2000 else text_content
    
    prompt = f"""Based on the following text, create {num_mc} multiple-choice questions and {num_tf} true/false questions.

Text content:
{content_snippet}

Format your response as JSON with this exact structure:
{{
    "multiple_choice": [
        {{
            "question": "Question text here?",
            "options": ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"],
            "correct_answer": "A",
            "explanation": "Why this answer is correct"
        }}
    ],
    "true_false": [
        {{
            "question": "Statement to evaluate",
            "correct_answer": "True",
            "explanation": "Explanation of the answer"
        }}
    ]
}}

Make questions directly based on the content provided. Ensure multiple choice questions have exactly 4 options labeled A, B, C, D."""
    
    payload = {
        "inputs": prompt,
        "parameters": {
            "max_new_tokens": 1500,
            "temperature": 0.7,
            "do_sample": True,
            "return_full_text": False
        }
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        
        result = response.json()
        
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get("generated_text", "")
        elif isinstance(result, dict):
            generated_text = result.get("generated_text", "")
        else:
            raise Exception("Unexpected response format from Hugging Face API")
        
        # Try to parse as JSON
        try:
            # Look for JSON in the response
            json_start = generated_text.find('{')
            json_end = generated_text.rfind('}') + 1
            
            if json_start != -1 and json_end > json_start:
                json_text = generated_text[json_start:json_end]
                questions_data = json.loads(json_text)
                return questions_data
            else:
                raise json.JSONDecodeError("No JSON found", "", 0)
                
        except json.JSONDecodeError:
            # Fallback: create structured questions from content
            return create_fallback_questions(content_snippet, num_mc, num_tf)
    
    except requests.exceptions.RequestException as e:
        raise Exception(f"API request failed: {str(e)}")

def create_fallback_questions(content, num_mc=5, num_tf=5):
    """
    Create fallback questions when API response isn't valid JSON
    """
    sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
    words = content.split()
    
    # Extract key terms (excluding common words)
    common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'when', 'what', 'with', 'this', 'that', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'were', 'will', 'your', 'about', 'after', 'before', 'other', 'right', 'their', 'there', 'these', 'which', 'would', 'could', 'should'}
    
    key_terms = [word.strip('.,!?;:') for word in words if len(word) > 4 and word.lower() not in common_words][:10]
    
    multiple_choice = []
    for i in range(min(num_mc, len(key_terms))):
        term = key_terms[i]
        multiple_choice.append({
            "question": f"Based on the content, what is the significance of {term}?",
            "options": [
                f"A) {term} is a central concept discussed in detail",
                f"B) {term} is mentioned briefly without explanation", 
                f"C) {term} contradicts the main ideas presented",
                f"D) {term} is not relevant to the topic"
            ],
            "correct_answer": "A",
            "explanation": f"The content discusses {term} as an important element of the topic."
        })
    
    true_false = []
    for i in range(min(num_tf, len(sentences))):
        sentence = sentences[i][:100] + "..." if len(sentences[i]) > 100 else sentences[i]
        true_false.append({
            "question": sentence,
            "correct_answer": "True",
            "explanation": "This statement is supported by the content provided."
        })
    
    return {
        "multiple_choice": multiple_choice,
        "true_false": true_false
    }

def render_quiz_form(questions_data):
    """
    Render the quiz questions in an editable form
    """
    st.header("📝 Generated Quiz Questions")
    
    if 'edited_questions' not in st.session_state:
        st.session_state.edited_questions = questions_data.copy()
    
    # Multiple Choice Questions
    st.subheader("Multiple Choice Questions")
    
    mc_questions = st.session_state.edited_questions.get('multiple_choice', [])
    
    for i, question in enumerate(mc_questions):
        with st.expander(f"MC Question {i+1}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Editable question
                new_question = st.text_area(
                    "Question:", 
                    value=question['question'],
                    key=f"mc_q_{i}",
                    height=100
                )
                
                # Editable options
                options = question.get('options', ['A)', 'B)', 'C)', 'D)'])
                new_options = []
                for j, option in enumerate(options):
                    new_option = st.text_input(
                        f"Option {chr(65+j)}:",
                        value=option,
                        key=f"mc_opt_{i}_{j}"
                    )
                    new_options.append(new_option)
                
                # Correct answer
                correct_answer = st.selectbox(
                    "Correct Answer:",
                    options=['A', 'B', 'C', 'D'],
                    index=['A', 'B', 'C', 'D'].index(question.get('correct_answer', 'A')),
                    key=f"mc_correct_{i}"
                )
                
                # Explanation
                explanation = st.text_area(
                    "Explanation:",
                    value=question.get('explanation', ''),
                    key=f"mc_exp_{i}",
                    height=80
                )
            
            with col2:
                st.write("**Actions:**")
                if st.button(f"Delete Question {i+1}", key=f"del_mc_{i}", type="secondary"):
                    mc_questions.pop(i)
                    st.rerun()
            
            # Update the question in session state
            st.session_state.edited_questions['multiple_choice'][i] = {
                'question': new_question,
                'options': new_options,
                'correct_answer': correct_answer,
                'explanation': explanation
            }
    
    # Add new MC question button
    if st.button("➕ Add Multiple Choice Question"):
        new_mc = {
            'question': 'New question?',
            'options': ['A) Option 1', 'B) Option 2', 'C) Option 3', 'D) Option 4'],
            'correct_answer': 'A',
            'explanation': 'Explanation here'
        }
        st.session_state.edited_questions['multiple_choice'].append(new_mc)
        st.rerun()
    
    st.divider()
    
    # True/False Questions
    st.subheader("True/False Questions")
    
    tf_questions = st.session_state.edited_questions.get('true_false', [])
    
    for i, question in enumerate(tf_questions):
        with st.expander(f"T/F Question {i+1}", expanded=True):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Editable question
                new_question = st.text_area(
                    "Statement:", 
                    value=question['question'],
                    key=f"tf_q_{i}",
                    height=100
                )
                
                # Correct answer
                correct_answer = st.selectbox(
                    "Correct Answer:",
                    options=['True', 'False'],
                    index=['True', 'False'].index(question.get('correct_answer', 'True')),
                    key=f"tf_correct_{i}"
                )
                
                # Explanation
                explanation = st.text_area(
                    "Explanation:",
                    value=question.get('explanation', ''),
                    key=f"tf_exp_{i}",
                    height=80
                )
            
            with col2:
                st.write("**Actions:**")
                if st.button(f"Delete Question {i+1}", key=f"del_tf_{i}", type="secondary"):
                    tf_questions.pop(i)
                    st.rerun()
            
            # Update the question in session state
            st.session_state.edited_questions['true_false'][i] = {
                'question': new_question,
                'correct_answer': correct_answer,
                'explanation': explanation
            }
    
    # Add new T/F question button
    if st.button("➕ Add True/False Question"):
        new_tf = {
            'question': 'New statement to evaluate',
            'correct_answer': 'True',
            'explanation': 'Explanation here'
        }
        st.session_state.edited_questions['true_false'].append(new_tf)
        st.rerun()

def export_quiz(questions_data, format_type="txt"):
    """
    Export quiz and answer key as downloadable file
    """
    if format_type == "txt":
        content = "QUIZ QUESTIONS\n" + "=" * 50 + "\n\n"
        
        # Multiple Choice Questions
        mc_questions = questions_data.get('multiple_choice', [])
        if mc_questions:
            content += "MULTIPLE CHOICE QUESTIONS:\n\n"
            for i, q in enumerate(mc_questions):
                content += f"{i+1}. {q['question']}\n"
                for option in q['options']:
                    content += f"   {option}\n"
                content += f"   Correct Answer: {q['correct_answer']}\n"
                content += f"   Explanation: {q['explanation']}\n\n"
        
        # True/False Questions
        tf_questions = questions_data.get('true_false', [])
        if tf_questions:
            content += "\nTRUE/FALSE QUESTIONS:\n\n"
            for i, q in enumerate(tf_questions):
                content += f"{len(mc_questions) + i + 1}. {q['question']}\n"
                content += f"   Correct Answer: {q['correct_answer']}\n"
                content += f"   Explanation: {q['explanation']}\n\n"
        
        return content.encode('utf-8')
    
    elif format_type == "docx":
        doc = Document()
        doc.add_heading('Quiz Questions', 0)
        
        # Multiple Choice Questions
        mc_questions = questions_data.get('multiple_choice', [])
        if mc_questions:
            doc.add_heading('Multiple Choice Questions', level=1)
            for i, q in enumerate(mc_questions):
                p = doc.add_paragraph(f"{i+1}. {q['question']}")
                p.style = 'Normal'
                
                for option in q['options']:
                    doc.add_paragraph(f"   {option}", style='List Bullet')
                
                doc.add_paragraph(f"Correct Answer: {q['correct_answer']}", style='Normal')
                doc.add_paragraph(f"Explanation: {q['explanation']}", style='Normal')
                doc.add_paragraph()  # Empty line
        
        # True/False Questions
        tf_questions = questions_data.get('true_false', [])
        if tf_questions:
            doc.add_heading('True/False Questions', level=1)
            for i, q in enumerate(tf_questions):
                doc.add_paragraph(f"{len(mc_questions) + i + 1}. {q['question']}")
                doc.add_paragraph(f"Correct Answer: {q['correct_answer']}")
                doc.add_paragraph(f"Explanation: {q['explanation']}")
                doc.add_paragraph()  # Empty line
        
        # Save to bytes
        doc_bytes = io.BytesIO()
        doc.save(doc_bytes)
        doc_bytes.seek(0)
        return doc_bytes.getvalue()

# Main App
def main():
    st.title("📚 AI Quiz Generator")
    st.markdown("Upload PDF files or paste article text to generate quiz questions with AI assistance")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # Check for API key
        hf_key = os.getenv("HUGGINGFACE_API_KEY")
        if hf_key:
            st.success("✅ Hugging Face API key configured")
        else:
            st.error("❌ HUGGINGFACE_API_KEY not found")
            st.info("Please set your Hugging Face API key in the environment variables.")
        
        st.subheader("Supported Content Types")
        st.write("📄 **PDF Files**: Chapters, research papers, textbooks")
        st.write("📰 **Articles**: Blog posts, news articles, web content")
        st.write("📖 **Text Content**: Any educational or informational text")
        
        st.subheader("Quiz Settings")
        num_mc = st.slider("Multiple Choice Questions", 1, 10, 5)
        num_tf = st.slider("True/False Questions", 1, 10, 5)
    
    # Input method selection
    st.header("📝 Choose Input Method")
    input_method = st.radio(
        "Select how you want to provide content:",
        ["📄 Upload PDF File", "📰 Paste Article Text"],
        horizontal=True
    )
    
    extracted_text = None
    
    if input_method == "📄 Upload PDF File":
        st.subheader("PDF File Upload")
        uploaded_file = st.file_uploader(
            "Choose a PDF file:",
            type=['pdf'],
            help="Upload a PDF containing a chapter or text content for quiz generation"
        )
        
        if uploaded_file is not None:
            try:
                # Extract text
                with st.spinner("Extracting text from PDF..."):
                    extracted_text = extract_text_from_pdf(uploaded_file)
                
                st.success(f"✅ Text extracted successfully! ({len(extracted_text)} characters)")
                
            except Exception as e:
                st.error(f"Error processing PDF: {str(e)}")
    
    elif input_method == "📰 Paste Article Text":
        st.subheader("Article Text Input")
        article_text = st.text_area(
            "Paste your article content here:",
            height=300,
            placeholder="Paste the article text, blog post, or any written content you want to create quiz questions from...",
            help="You can paste articles from websites, documents, or any text content"
        )
        
        if article_text:
            try:
                extracted_text = extract_text_from_article(article_text)
                st.success(f"✅ Article processed successfully! ({len(extracted_text)} characters)")
                
            except Exception as e:
                st.error(f"Error processing article: {str(e)}")
    
    # Show preview and generate questions if text is available
    if extracted_text:
        # Show preview
        with st.expander("📖 Preview Content"):
            st.text_area("Content:", extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text, height=200, disabled=True)
        
        # Generate questions
        if st.button("🎯 Generate Quiz Questions", type="primary"):
            try:
                with st.spinner("Generating quiz questions with AI..."):
                    questions_data = generate_questions_with_hf(extracted_text, num_mc, num_tf)
                
                st.success("✅ Quiz questions generated successfully!")
                
                # Store in session state
                st.session_state.questions_generated = True
                st.session_state.original_questions = questions_data
                st.session_state.edited_questions = questions_data.copy()
                
            except Exception as e:
                st.error(f"Error generating questions: {str(e)}")
    
    # Display and edit questions
    if st.session_state.get('questions_generated', False):
        render_quiz_form(st.session_state.edited_questions)
        
        # Export options
        st.divider()
        st.header("📥 Export Quiz")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            txt_content = export_quiz(st.session_state.edited_questions, "txt")
            st.download_button(
                label="📄 Download as TXT",
                data=txt_content,
                file_name="quiz_questions.txt",
                mime="text/plain",
                type="secondary"
            )
        
        with col2:
            docx_content = export_quiz(st.session_state.edited_questions, "docx")
            st.download_button(
                label="📝 Download as DOCX",
                data=docx_content,
                file_name="quiz_questions.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                type="secondary"
            )
        
        with col3:
            if st.button("🔄 Reset Quiz", type="secondary"):
                if 'original_questions' in st.session_state:
                    st.session_state.edited_questions = st.session_state.original_questions.copy()
                    st.rerun()

if __name__ == "__main__":
    main()