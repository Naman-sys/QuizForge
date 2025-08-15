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

def generate_questions_with_local_ai(text_content, num_mc=5, num_tf=5):
    """
    Generate quiz questions using local content analysis without external APIs
    """
    return create_intelligent_questions(text_content, num_mc, num_tf)

def create_intelligent_questions(content, num_mc=5, num_tf=5):
    """
    Create intelligent quiz questions using local content analysis
    """
    import re
    import random
    
    # Process content into sentences and extract key information
    sentences = [s.strip() for s in re.split(r'[.!?]+', content) if len(s.strip()) > 20]
    words = content.split()
    paragraphs = [p.strip() for p in content.split('\n\n') if len(p.strip()) > 50]
    
    # Extract key terms, numbers, and facts
    common_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'she', 'use', 'way', 'when', 'what', 'with', 'this', 'that', 'have', 'from', 'they', 'know', 'want', 'been', 'good', 'much', 'some', 'time', 'very', 'were', 'will', 'your', 'about', 'after', 'before', 'other', 'right', 'their', 'there', 'these', 'which', 'would', 'could', 'should', 'often', 'called'}
    
    # Extract key terms (proper nouns, important concepts)
    key_terms = []
    for word in words:
        clean_word = re.sub(r'[^\w]', '', word)
        if (len(clean_word) > 4 and 
            clean_word.lower() not in common_words and
            (clean_word[0].isupper() or len(clean_word) > 7)):
            key_terms.append(clean_word)
    
    # Remove duplicates and take top terms
    key_terms = list(dict.fromkeys(key_terms))[:15]
    
    # Extract numbers and measurements
    numbers = re.findall(r'\d+(?:\.\d+)?(?:\s*million|billion|thousand|%|km|meters|years|species)?', content)
    
    # Generate Multiple Choice Questions
    multiple_choice = []
    
    # Question types based on content analysis
    question_types = [
        ("definition", "What is"),
        ("significance", "What is the significance of"),
        ("function", "What role does"),
        ("characteristic", "Which characteristic describes"),
        ("location", "Where is"),
        ("quantity", "How many/much")
    ]
    
    for i in range(min(num_mc, len(key_terms))):
        term = key_terms[i]
        q_type, q_start = random.choice(question_types)
        
        # Find context for this term
        context_sentences = [s for s in sentences if term.lower() in s.lower()]
        context = context_sentences[0] if context_sentences else f"Information about {term}"
        
        # Generate question based on term and context
        if q_type == "definition":
            question = f"{q_start} {term}?"
            correct_option = f"An important concept mentioned in the text"
            wrong_options = [
                f"A minor detail not discussed",
                f"Something unrelated to the topic",
                f"An outdated concept"
            ]
        elif q_type == "significance":
            question = f"{q_start} {term} in this context?"
            correct_option = f"It plays a crucial role in the topic discussed"
            wrong_options = [
                f"It has minimal importance",
                f"It contradicts the main ideas",
                f"It is only mentioned in passing"
            ]
        else:
            question = f"{q_start} {term} contribute to the topic?"
            correct_option = f"It is a key element in understanding the subject"
            wrong_options = [
                f"It provides contradictory information",
                f"It is irrelevant to the main discussion",
                f"It offers only background context"
            ]
        
        # Shuffle options
        all_options = [correct_option] + wrong_options
        random.shuffle(all_options)
        correct_index = all_options.index(correct_option)
        correct_letter = ['A', 'B', 'C', 'D'][correct_index]
        
        formatted_options = [f"{['A', 'B', 'C', 'D'][j]}) {opt}" for j, opt in enumerate(all_options)]
        
        multiple_choice.append({
            "question": question,
            "options": formatted_options,
            "correct_answer": correct_letter,
            "explanation": f"Based on the content, {term} is discussed as {correct_option.lower()}."
        })
    
    # Generate True/False Questions
    true_false = []
    
    # Use actual sentences from content for true statements
    for i in range(min(num_tf, len(sentences))):
        sentence = sentences[i]
        
        # Create true statement (directly from content)
        if random.choice([True, False]) and len(true_false) < num_tf // 2:
            # True statement
            statement = sentence[:150] + "..." if len(sentence) > 150 else sentence
            true_false.append({
                "question": statement,
                "correct_answer": "True",
                "explanation": "This statement is directly supported by the provided content."
            })
        else:
            # False statement (modify the sentence)
            if key_terms:
                term = random.choice(key_terms)
                # Create a false statement by negation or modification
                false_statement = f"{term} is not mentioned or discussed in the content"
                if term.lower() in content.lower():
                    false_statement = f"{term} has no significance to the topic discussed"
                
                true_false.append({
                    "question": false_statement,
                    "correct_answer": "False",
                    "explanation": f"This is incorrect because {term} is actually discussed in the content as an important element."
                })
    
    # Ensure we have enough questions
    while len(multiple_choice) < num_mc and key_terms:
        remaining_terms = [t for t in key_terms if not any(t in q["question"] for q in multiple_choice)]
        if not remaining_terms:
            break
        
        term = remaining_terms[0]
        multiple_choice.append({
            "question": f"According to the content, what can be said about {term}?",
            "options": [
                f"A) {term} is a central topic in the discussion",
                f"B) {term} is barely mentioned",
                f"C) {term} is criticized in the text",
                f"D) {term} is completely irrelevant"
            ],
            "correct_answer": "A",
            "explanation": f"The content discusses {term} as part of the main topic."
        })
    
    while len(true_false) < num_tf and sentences:
        remaining_sentences = [s for s in sentences if not any(s[:50] in q["question"] for q in true_false)]
        if not remaining_sentences:
            break
        
        sentence = remaining_sentences[0][:100]
        true_false.append({
            "question": f"The content states that {sentence.lower()}",
            "correct_answer": "True",
            "explanation": "This statement reflects information presented in the content."
        })
    
    return {
        "multiple_choice": multiple_choice[:num_mc],
        "true_false": true_false[:num_tf]
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
        
        st.subheader("Local AI Generation")
        st.success("✅ Local question generation enabled")
        st.info("No external API required - questions generated using intelligent content analysis")
        
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
                with st.spinner("Analyzing content and generating quiz questions..."):
                    questions_data = generate_questions_with_local_ai(extracted_text, num_mc, num_tf)
                
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