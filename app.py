import streamlit as st
import json
from quiz_generator import QuizGenerator
from file_processor import FileProcessor

# Initialize session state
if 'quiz_data' not in st.session_state:
    st.session_state.quiz_data = None
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'quiz_completed' not in st.session_state:
    st.session_state.quiz_completed = False
if 'score' not in st.session_state:
    st.session_state.score = 0

st.title("🧠 AI-Powered Quiz Generator")
st.markdown("Generate customizable quizzes from your data with AI")

# Initialize components
quiz_gen = QuizGenerator()
file_proc = FileProcessor()

# Sidebar for configuration
st.sidebar.header("Quiz Configuration")

# Data input section
st.header("📝 Input Your Data")

input_method = st.radio(
    "Choose input method:",
    ["Text Input", "File Upload"],
    horizontal=True
)

input_data = ""

if input_method == "Text Input":
    input_data = st.text_area(
        "Enter your text content:",
        height=200,
        placeholder="Paste your content here... (articles, notes, study materials, etc.)"
    )
elif input_method == "File Upload":
    uploaded_file = st.file_uploader(
        "Upload a file:",
        type=['txt', 'pdf', 'docx'],
        help="Supported formats: TXT, PDF, DOCX"
    )
    
    if uploaded_file is not None:
        try:
            with st.spinner("Processing file..."):
                input_data = file_proc.process_file(uploaded_file)
            st.success(f"File processed successfully! ({len(input_data)} characters)")
            
            # Show preview of extracted text
            with st.expander("Preview extracted text"):
                st.text(input_data[:500] + "..." if len(input_data) > 500 else input_data)
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")

# Quiz configuration
if input_data:
    st.header("⚙️ Quiz Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        difficulty = st.selectbox(
            "Difficulty Level:",
            ["Easy", "Medium", "Hard"],
            help="Easy: Basic recall questions, Medium: Understanding and application, Hard: Analysis and synthesis"
        )
    
    with col2:
        num_questions = st.slider(
            "Number of Questions:",
            min_value=3,
            max_value=20,
            value=5,
            help="Select how many questions to generate"
        )
    
    # Question type selection
    question_types = st.multiselect(
        "Question Types:",
        ["Multiple Choice", "True/False", "Short Answer"],
        default=["Multiple Choice", "True/False"],
        help="Select the types of questions to include in your quiz"
    )
    
    if not question_types:
        st.warning("Please select at least one question type.")
    
    # Generate quiz button
    if st.button("🎯 Generate Quiz", type="primary", disabled=not question_types):
        if len(input_data.strip()) < 50:
            st.error("Please provide more content (at least 50 characters) to generate meaningful questions.")
        else:
            try:
                with st.spinner("Generating quiz questions with AI..."):
                    quiz_data = quiz_gen.generate_quiz(
                        input_data, 
                        difficulty, 
                        num_questions, 
                        question_types
                    )
                
                if quiz_data and 'questions' in quiz_data:
                    st.session_state.quiz_data = quiz_data
                    st.session_state.current_question = 0
                    st.session_state.user_answers = {}
                    st.session_state.quiz_completed = False
                    st.session_state.score = 0
                    st.success(f"Quiz generated successfully! {len(quiz_data['questions'])} questions created.")
                    st.rerun()
                else:
                    st.error("Failed to generate quiz. Please try again with different content.")
            
            except Exception as e:
                st.error(f"Error generating quiz: {str(e)}")

# Display quiz
if st.session_state.quiz_data and not st.session_state.quiz_completed:
    st.header("📋 Quiz Time!")
    
    quiz = st.session_state.quiz_data
    questions = quiz['questions']
    current_q = st.session_state.current_question
    
    if current_q < len(questions):
        question = questions[current_q]
        
        # Progress bar
        progress = (current_q + 1) / len(questions)
        st.progress(progress)
        st.write(f"Question {current_q + 1} of {len(questions)}")
        
        # Display question
        st.subheader(f"Q{current_q + 1}: {question['question']}")
        
        # Handle different question types
        user_answer = None
        if question['type'] == 'Multiple Choice':
            user_answer = st.radio(
                "Select your answer:",
                question['options'],
                key=f"q_{current_q}",
                index=None
            )
        
        elif question['type'] == 'True/False':
            user_answer = st.radio(
                "Select your answer:",
                ["True", "False"],
                key=f"q_{current_q}",
                index=None
            )
        
        elif question['type'] == 'Short Answer':
            user_answer = st.text_input(
                "Enter your answer:",
                key=f"q_{current_q}",
                placeholder="Type your answer here..."
            )
        
        # Navigation buttons
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            if current_q > 0:
                if st.button("⬅️ Previous"):
                    st.session_state.current_question -= 1
                    st.rerun()
        
        with col2:
            if user_answer is not None and user_answer != "":
                if st.button("💾 Save Answer", type="secondary"):
                    st.session_state.user_answers[current_q] = user_answer
                    st.success("Answer saved!")
        
        with col3:
            if user_answer is not None and user_answer != "":
                if current_q < len(questions) - 1:
                    if st.button("Next ➡️"):
                        st.session_state.user_answers[current_q] = user_answer
                        st.session_state.current_question += 1
                        st.rerun()
                else:
                    if st.button("🏁 Finish Quiz", type="primary"):
                        st.session_state.user_answers[current_q] = user_answer
                        st.session_state.quiz_completed = True
                        
                        # Calculate score
                        score = quiz_gen.calculate_score(
                            st.session_state.quiz_data,
                            st.session_state.user_answers
                        )
                        st.session_state.score = score
                        st.rerun()

# Display results
if st.session_state.quiz_completed and st.session_state.quiz_data:
    st.header("🎉 Quiz Results")
    
    score_data = st.session_state.score
    total_questions = len(st.session_state.quiz_data['questions'])
    correct_answers = score_data['correct'] if isinstance(score_data, dict) else 0
    percentage = (correct_answers / total_questions) * 100
    
    # Score display
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Score", f"{correct_answers}/{total_questions}")
    
    with col2:
        st.metric("Percentage", f"{percentage:.1f}%")
    
    with col3:
        if percentage >= 80:
            grade = "Excellent! 🌟"
        elif percentage >= 60:
            grade = "Good! 👍"
        elif percentage >= 40:
            grade = "Fair 📚"
        else:
            grade = "Needs Improvement 💪"
        st.metric("Grade", grade)
    
    # Detailed results
    st.subheader("📊 Detailed Results")
    
    questions = st.session_state.quiz_data['questions']
    user_answers = st.session_state.user_answers
    
    for i, question in enumerate(questions):
        with st.expander(f"Question {i+1}: {question['question'][:50]}..."):
            st.write(f"**Question:** {question['question']}")
            
            if question['type'] in ['Multiple Choice', 'True/False']:
                st.write(f"**Correct Answer:** {question['correct_answer']}")
                user_ans = user_answers.get(i, "Not answered")
                st.write(f"**Your Answer:** {user_ans}")
                
                if user_ans == question['correct_answer']:
                    st.success("✅ Correct!")
                else:
                    st.error("❌ Incorrect")
            
            elif question['type'] == 'Short Answer':
                st.write(f"**Expected Answer:** {question['correct_answer']}")
                user_ans = user_answers.get(i, "Not answered")
                st.write(f"**Your Answer:** {user_ans}")
                
                # For short answers, show if it was marked correct
                if isinstance(score_data, dict) and i in score_data.get('short_answer_scores', {}):
                    if score_data['short_answer_scores'][i]:
                        st.success("✅ Correct!")
                    else:
                        st.error("❌ Incorrect")
            
            if 'explanation' in question and question['explanation']:
                st.info(f"**Explanation:** {question['explanation']}")
    
    # Restart button
    if st.button("🔄 Generate New Quiz", type="primary"):
        st.session_state.quiz_data = None
        st.session_state.current_question = 0
        st.session_state.user_answers = {}
        st.session_state.quiz_completed = False
        st.session_state.score = 0
        st.rerun()

# Footer
st.markdown("---")
st.markdown("💡 **Tip:** For best results, provide detailed and comprehensive content for quiz generation.")
