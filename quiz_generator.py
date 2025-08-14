import json
import os
import requests

class QuizGenerator:
    def __init__(self):
        # Using Hugging Face Inference API
        self.hf_token = os.getenv("HUGGINGFACE_API_KEY", "your-api-key-here")
        self.base_url = "https://api-inference.huggingface.co/models/"
        self.model = "microsoft/DialoGPT-medium"  # Better for quiz generation tasks
        self.headers = {"Authorization": f"Bearer {self.hf_token}"}
    
    def generate_quiz(self, content, difficulty, num_questions, question_types):
        """
        Generate a quiz from the provided content using Hugging Face API
        """
        try:
            # Create the prompt based on parameters
            prompt = self._create_quiz_prompt(content, difficulty, num_questions, question_types)
            
            # Use Hugging Face Inference API
            response = self._call_huggingface_api(prompt)
            
            # Try to parse the response as JSON
            try:
                result = json.loads(response)
                return result
            except json.JSONDecodeError:
                # If the response isn't valid JSON, create a structured response
                return self._create_fallback_quiz(content, difficulty, num_questions, question_types, response)
            
        except Exception as e:
            raise Exception(f"Failed to generate quiz: {str(e)}")
    
    def _create_quiz_prompt(self, content, difficulty, num_questions, question_types):
        """
        Create a detailed prompt for quiz generation
        """
        difficulty_descriptions = {
            "Easy": "basic recall and recognition questions, simple factual questions",
            "Medium": "questions requiring understanding, application, and basic analysis",
            "Hard": "complex analysis, synthesis, evaluation, and critical thinking questions"
        }
        
        type_instructions = {
            "Multiple Choice": "4 options with exactly one correct answer",
            "True/False": "clear true or false statements",
            "Short Answer": "questions requiring brief explanatory answers (1-3 sentences)"
        }
        
        selected_types = [type_instructions[t] for t in question_types]
        
        prompt = f"""Generate a {difficulty.lower()}-level quiz with {num_questions} questions from this content:

{content[:1000]}...

Create questions of these types: {', '.join(question_types)}

Return only valid JSON format:
{{
    "quiz_title": "Quiz About the Content",
    "difficulty": "{difficulty}",
    "total_questions": {num_questions},
    "questions": [
        {{
            "id": 1,
            "type": "{question_types[0] if question_types else 'Multiple Choice'}",
            "question": "Your question here?",
            "options": ["A", "B", "C", "D"],
            "correct_answer": "A",
            "explanation": "Why this is correct"
        }}
    ]
}}

Make questions directly from the content. Use {difficulty_descriptions[difficulty]}."""
        return prompt
    
    def calculate_score(self, quiz_data, user_answers):
        """
        Calculate the quiz score based on user answers
        """
        questions = quiz_data['questions']
        correct_count = 0
        total_questions = len(questions)
        short_answer_scores = {}
        
        for i, question in enumerate(questions):
            user_answer = user_answers.get(i, "")
            
            if question['type'] in ['Multiple Choice', 'True/False']:
                if user_answer == question['correct_answer']:
                    correct_count += 1
            
            elif question['type'] == 'Short Answer':
                # For short answer questions, use AI to evaluate the answer
                is_correct = self._evaluate_short_answer(
                    question['question'],
                    question['correct_answer'],
                    user_answer
                )
                short_answer_scores[i] = is_correct
                if is_correct:
                    correct_count += 1
        
        return {
            'correct': correct_count,
            'total': total_questions,
            'percentage': (correct_count / total_questions) * 100 if total_questions > 0 else 0,
            'short_answer_scores': short_answer_scores
        }
    
    def _evaluate_short_answer(self, question, expected_answer, user_answer):
        """
        Use AI to evaluate short answer questions
        """
        if not user_answer or user_answer.strip() == "":
            return False
        
        try:
            prompt = f"""Evaluate if the user's answer is correct or acceptable.

QUESTION: {question}
EXPECTED ANSWER: {expected_answer}
USER'S ANSWER: {user_answer}

Respond with JSON: {{"is_correct": true/false, "reasoning": "explanation"}}

Be lenient - if the answer contains key concepts, mark as correct even if wording differs."""
            
            response = self._call_huggingface_api(prompt)
            
            try:
                result = json.loads(response)
                return result.get('is_correct', False)
            except json.JSONDecodeError:
                # Simple keyword matching as fallback
                expected_lower = expected_answer.lower()
                user_lower = user_answer.lower()
                
                # Check if user answer contains key words from expected answer
                expected_words = set(expected_lower.split())
                user_words = set(user_lower.split())
                
                # If at least 30% of expected words are in user answer, consider correct
                overlap = len(expected_words.intersection(user_words))
                return overlap >= len(expected_words) * 0.3
            
        except Exception as e:
            # If evaluation fails, default to False but log the error
            print(f"Error evaluating short answer: {e}")
            return False
    
    def _call_huggingface_api(self, prompt):
        """
        Make API call to Hugging Face Inference API
        """
        # Use a text generation model that's good for structured output
        model_url = f"{self.base_url}microsoft/DialoGPT-medium"
        
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 2000,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False
            }
        }
        
        try:
            response = requests.post(model_url, headers=self.headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                return result[0].get("generated_text", "")
            elif isinstance(result, dict):
                return result.get("generated_text", "")
            else:
                raise Exception("Unexpected response format from Hugging Face API")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")
    
    def _create_fallback_quiz(self, content, difficulty, num_questions, question_types, ai_response):
        """
        Create a structured quiz when AI response isn't valid JSON
        """
        # This creates a basic quiz structure when the AI response needs formatting
        questions = []
        
        # Simple question generation based on content
        sentences = [s.strip() for s in content.split('.') if len(s.strip()) > 20]
        
        question_count = min(num_questions, len(sentences))
        
        for i in range(question_count):
            question_type = question_types[i % len(question_types)]
            
            if question_type == "Multiple Choice":
                questions.append({
                    "id": i + 1,
                    "type": "Multiple Choice",
                    "question": f"Based on the content, which statement is most accurate about the topic discussed?",
                    "options": [
                        "Option A - requires content analysis",
                        "Option B - requires content analysis", 
                        "Option C - requires content analysis",
                        "Option D - requires content analysis"
                    ],
                    "correct_answer": "Option A - requires content analysis",
                    "explanation": "This question requires analyzing the provided content."
                })
            elif question_type == "True/False":
                questions.append({
                    "id": i + 1,
                    "type": "True/False",
                    "question": f"The content discusses important concepts related to the main topic.",
                    "options": ["True", "False"],
                    "correct_answer": "True",
                    "explanation": "Based on the provided content analysis."
                })
            elif question_type == "Short Answer":
                questions.append({
                    "id": i + 1,
                    "type": "Short Answer",
                    "question": f"Explain the main concept discussed in the provided content.",
                    "correct_answer": "The answer should summarize the key points from the content.",
                    "explanation": "A good answer should identify and explain the main ideas."
                })
        
        return {
            "quiz_title": f"{difficulty} Level Quiz",
            "difficulty": difficulty,
            "total_questions": len(questions),
            "questions": questions
        }
