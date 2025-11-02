import google.generativeai as genai
from django.conf import settings
import json
import logging
import random

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_assessment_quiz(course_name, user=None):
    """
    Generate dynamic personalized quiz using Gemini API (10 questions)
    Different questions generated each time for the same topic
    """
    
    # Create unique seed for randomization
    seed = random.randint(10000, 99999)
    
    prompt = f"""You are an expert educator creating assessment questions for personalized learning.

TOPIC/COURSE: {course_name}
SEED: {seed}

CRITICAL INSTRUCTIONS:
1. Generate exactly 10 NEW, UNIQUE multiple-choice questions about: {course_name}
2. Each API call must produce DIFFERENT questions (vary examples, scenarios, sub-topics)
3. DO NOT repeat questions from previous generations
4. Mix difficulty: 3 beginner (basic concepts), 5 intermediate (applications), 2 advanced (edge cases)
5. Include code snippets if relevant to {course_name}

OUTPUT: Return ONLY valid JSON (no markdown, no code blocks, no text before/after):
{{
  "quiz_metadata": {{
    "course_name": "{course_name}",
    "total_questions": 10,
    "estimated_time_minutes": 10,
    "seed": {seed}
  }},
  "questions": [
    {{
      "question_id": "q1",
      "question_number": 1,
      "difficulty": "beginner",
      "topic": "Basic Concepts of {course_name}",
      "question_text": "What is the primary purpose of {course_name}?",
      "code_snippet": "",
      "options": {{
        "A": "Option A - detailed answer",
        "B": "Option B - detailed answer",
        "C": "Option C - detailed answer",
        "D": "Option D - detailed answer"
      }},
      "correct_answer": "A",
      "explanation": "Detailed explanation of why A is correct",
      "concept_tested": "Understanding fundamentals"
    }},
    {{
      "question_id": "q2",
      "question_number": 2,
      "difficulty": "beginner",
      "topic": "Introduction to {course_name}",
      "question_text": "Question about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "B",
      "explanation": "Explanation",
      "concept_tested": "Key concept"
    }},
    {{
      "question_id": "q3",
      "question_number": 3,
      "difficulty": "beginner",
      "topic": "Fundamentals of {course_name}",
      "question_text": "Another beginner question about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "C",
      "explanation": "Explanation",
      "concept_tested": "Core understanding"
    }},
    {{
      "question_id": "q4",
      "question_number": 4,
      "difficulty": "intermediate",
      "topic": "Practical Applications of {course_name}",
      "question_text": "Practical question about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Explanation",
      "concept_tested": "Application skills"
    }},
    {{
      "question_id": "q5",
      "question_number": 5,
      "difficulty": "intermediate",
      "topic": "Implementation of {course_name}",
      "question_text": "How would you implement {course_name} in practice?",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "B",
      "explanation": "Explanation",
      "concept_tested": "Practical implementation"
    }},
    {{
      "question_id": "q6",
      "question_number": 6,
      "difficulty": "intermediate",
      "topic": "Best Practices in {course_name}",
      "question_text": "Best practice question about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "C",
      "explanation": "Explanation",
      "concept_tested": "Best practices"
    }},
    {{
      "question_id": "q7",
      "question_number": 7,
      "difficulty": "intermediate",
      "topic": "Advanced Concepts of {course_name}",
      "question_text": "Intermediate challenge about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "D",
      "explanation": "Explanation",
      "concept_tested": "Problem solving"
    }},
    {{
      "question_id": "q8",
      "question_number": 8,
      "difficulty": "intermediate",
      "topic": "Real-world Applications of {course_name}",
      "question_text": "Real-world scenario about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "A",
      "explanation": "Explanation",
      "concept_tested": "Applied knowledge"
    }},
    {{
      "question_id": "q9",
      "question_number": 9,
      "difficulty": "advanced",
      "topic": "Expert Knowledge in {course_name}",
      "question_text": "Advanced edge case about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "B",
      "explanation": "Explanation",
      "concept_tested": "Advanced understanding"
    }},
    {{
      "question_id": "q10",
      "question_number": 10,
      "difficulty": "advanced",
      "topic": "Mastery of {course_name}",
      "question_text": "Expert-level question about {course_name}",
      "code_snippet": "",
      "options": {{
        "A": "Option A",
        "B": "Option B",
        "C": "Option C",
        "D": "Option D"
      }},
      "correct_answer": "C",
      "explanation": "Explanation",
      "concept_tested": "Mastery level"
    }}
  ]
}}

Remember: Output ONLY the JSON object above. No explanations, no markdown, no code blocks."""

    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Remove markdown code blocks if present
        if '```':
            parts = response_text.split('```')
            response_text = parts[1] if len(parts) > 1 else response_text
            if response_text.startswith('json'):
                response_text = response_text[4:]
            response_text = response_text.strip()
        
        quiz_data = json.loads(response_text)
        
        if validate_quiz_structure(quiz_data):
            logger.info(f"Dynamic quiz generated for: {course_name}")
            return quiz_data
        else:
            logger.warning(f"Generated quiz validation failed for {course_name}")
            return None
            
    except Exception as e:
        logger.error(f"Quiz generation error for '{course_name}': {str(e)}")
        return None


def validate_quiz_structure(quiz_data):
    """Validate generated quiz meets requirements"""
    
    try:
        if 'quiz_metadata' not in quiz_data or 'questions' not in quiz_data:
            return False
        
        questions = quiz_data['questions']
        
        if len(questions) != 10:
            return False
        
        required_fields = ['question_id', 'difficulty', 'topic', 'question_text', 
                           'options', 'correct_answer', 'explanation']
        
        for q in questions:
            if not all(field in q for field in required_fields):
                return False
            
            if not all(opt in q['options'] for opt in ['A', 'B', 'C', 'D']):
                return False
            
            if q['correct_answer'] not in ['A', 'B', 'C', 'D']:
                return False
        
        return True
    except:
        return False
