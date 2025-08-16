import json
import logging
import os
import google.generativeai as genai
from typing import Dict, List, Any

class GeminiQuizGenerator:
    def __init__(self):
        """Initialize Gemini client with API key"""
        api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = "gemini-1.5-flash"

    def generate_quiz(self, content: str, difficulty: str, num_mc: int, num_tf: int) -> Dict[str, Any]:
        """
        Generate quiz questions using Gemini AI
        
        Args:
            content: The text content to generate questions from
            difficulty: 'easy', 'medium', or 'hard'
            num_mc: Number of multiple choice questions
            num_tf: Number of true/false questions
            
        Returns:
            Dictionary with generated quiz questions
        """
        try:
            # Create the prompt for Gemini
            prompt = self._create_quiz_prompt(content, difficulty, num_mc, num_tf)
            
            # Call Gemini API
            model = genai.GenerativeModel(self.model)
            
            # Configure generation parameters
            generation_config = genai.GenerationConfig(
                temperature=0.7,
                max_output_tokens=4000
            )
            
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Parse the JSON response
            if response.text:
                response_text = response.text.strip()
                
                # Try to extract JSON from response if it's wrapped in markdown
                if '```json' in response_text:
                    start = response_text.find('```json') + 7
                    end = response_text.find('```', start)
                    if end != -1:
                        response_text = response_text[start:end].strip()
                elif '```' in response_text:
                    start = response_text.find('```') + 3
                    end = response_text.find('```', start)
                    if end != -1:
                        response_text = response_text[start:end].strip()
                
                # Parse JSON
                quiz_data = json.loads(response_text)
                return self._validate_and_format_quiz(quiz_data, num_mc, num_tf)
            else:
                raise Exception("Empty response from Gemini API")
                
        except json.JSONDecodeError as e:
            raise Exception(f"Failed to parse Gemini response as JSON: {str(e)}")
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")

    def _create_quiz_prompt(self, content: str, difficulty: str, num_mc: int, num_tf: int) -> str:
        """Create a detailed prompt for quiz generation"""
        
        difficulty_guidelines = {
            "easy": {
                "description": "Basic recall and recognition questions with simple vocabulary",
                "focus": "Factual information, definitions, and straightforward concepts",
                "complexity": "Elementary level understanding"
            },
            "medium": {
                "description": "Questions requiring understanding, application, and basic analysis",
                "focus": "Connecting concepts, explaining relationships, and applying knowledge",
                "complexity": "High school to undergraduate level"
            },
            "hard": {
                "description": "Complex analysis, synthesis, evaluation, and critical thinking",
                "focus": "Advanced reasoning, comparing theories, and drawing conclusions",
                "complexity": "Advanced undergraduate to graduate level"
            }
        }
        
        guidelines = difficulty_guidelines.get(difficulty, difficulty_guidelines["medium"])
        
        # Truncate content if too long (keep within token limits)
        max_content_length = 1500
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""You are an expert educational quiz creator. Create a {difficulty} level quiz based on the provided content.

CONTENT TO ANALYZE:
{content}

QUIZ REQUIREMENTS:
- Generate {num_mc} multiple choice questions
- Generate {num_tf} true/false questions
- Difficulty Level: {difficulty.upper()}
- {guidelines['description']}
- Focus on: {guidelines['focus']}
- Complexity: {guidelines['complexity']}

FORMATTING INSTRUCTIONS:
- Each multiple choice question must have exactly 4 options (A, B, C, D)
- Only ONE option should be correct
- True/false questions should be clear statements that are definitively true or false
- Include helpful explanations for learning
- Base ALL questions strictly on the provided content
- Avoid questions that require external knowledge
- IMPORTANT: Response must be valid JSON only, no extra text or markdown formatting

OUTPUT FORMAT (JSON ONLY):
{{
    "multiple_choice": [
        {{
            "question": "Clear, well-formed question?",
            "options": ["A) First option", "B) Second option", "C) Third option", "D) Fourth option"],
            "correct_answer": "A",
            "explanation": "Clear explanation of why this answer is correct"
        }}
    ],
    "true_false": [
        {{
            "question": "Clear statement that can be definitively judged as true or false.",
            "correct_answer": "True",
            "explanation": "Clear explanation of why this statement is true/false"
        }}
    ]
}}

Generate exactly {num_mc} multiple choice and {num_tf} true/false questions. Return ONLY the JSON, no other text."""

        return prompt

    def _validate_and_format_quiz(self, quiz_data: Dict[str, Any], expected_mc: int, expected_tf: int) -> Dict[str, Any]:
        """Validate and format the quiz data from Gemini"""
        
        formatted_quiz = {
            "multiple_choice": [],
            "true_false": []
        }
        
        # Process multiple choice questions
        mc_questions = quiz_data.get("multiple_choice", [])
        for i, q in enumerate(mc_questions[:expected_mc]):  # Limit to expected number
            if self._validate_mc_question(q):
                formatted_quiz["multiple_choice"].append({
                    "question": q["question"],
                    "options": q["options"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q.get("explanation", "No explanation provided")
                })
        
        # Process true/false questions
        tf_questions = quiz_data.get("true_false", [])
        for i, q in enumerate(tf_questions[:expected_tf]):  # Limit to expected number
            if self._validate_tf_question(q):
                formatted_quiz["true_false"].append({
                    "question": q["question"],
                    "correct_answer": q["correct_answer"],
                    "explanation": q.get("explanation", "No explanation provided")
                })
        
        return formatted_quiz

    def _validate_mc_question(self, question: Dict[str, Any]) -> bool:
        """Validate multiple choice question format"""
        required_fields = ["question", "options", "correct_answer"]
        
        if not all(field in question for field in required_fields):
            return False
        
        if not isinstance(question["options"], list) or len(question["options"]) != 4:
            return False
        
        # Check if correct answer matches any option (handle both letter format like "A" and full option like "A) First option")
        correct_answer = question["correct_answer"]
        options = question["options"]
        
        # If correct answer is just a letter, find the matching option
        if len(correct_answer) == 1 and correct_answer in ['A', 'B', 'C', 'D']:
            # Find the option that starts with this letter
            matching_options = [opt for opt in options if opt.startswith(f"{correct_answer})")]
            if not matching_options:
                return False
        elif correct_answer not in options:
            return False
        
        return True

    def _validate_tf_question(self, question: Dict[str, Any]) -> bool:
        """Validate true/false question format"""
        required_fields = ["question", "correct_answer"]
        
        if not all(field in question for field in required_fields):
            return False
        
        if question["correct_answer"].lower() not in ["true", "false"]:
            return False
        
        return True

    def test_connection(self) -> bool:
        """Test if Gemini API connection is working"""
        try:
            model = genai.GenerativeModel(self.model)
            response = model.generate_content(
                "Say 'Hello' in JSON format: {\"message\": \"Hello\"}"
            )
            return response.text is not None
        except Exception:
            return False