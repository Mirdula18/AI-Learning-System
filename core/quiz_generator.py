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
    
    # Try LLM generation first
    quiz_data = try_llm_generation(course_name)
    
    # If LLM fails, use reliable fallback
    if not quiz_data:
        logger.warning(f"LLM failed for {course_name}, using fallback")
        quiz_data = generate_fallback_quiz(course_name)
    
    return quiz_data


def try_llm_generation(course_name):
    """Try to generate quiz using LLM"""
    try:
        prompt = f"""Generate exactly 10 multiple-choice questions about {course_name}.
Return ONLY this JSON format with no other text:
{{"questions": [{{"question_id": "q1", "question_number": 1, "difficulty": "beginner", "topic": "{course_name} Basics", "question_text": "What is a key concept of {course_name}?", "code_snippet": "", "options": {{"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"}}, "correct_answer": "A", "explanation": "Explanation here", "concept_tested": "Concept"}}]}}"""
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response
        if '```':
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        response_text = response_text.strip()
        
        # Parse JSON
        quiz_data = json.loads(response_text)
        
        # Basic validation
        if 'questions' in quiz_data and len(quiz_data['questions']) >= 5:
            logger.info(f"LLM quiz generated for: {course_name}")
            return format_quiz_data(quiz_data, course_name)
        
        return None
        
    except Exception as e:
        logger.error(f"LLM generation failed for {course_name}: {str(e)}")
        return None


def generate_fallback_quiz(course_name):
    """Generate reliable fallback quiz"""
    return {
        "quiz_metadata": {
            "course_name": course_name,
            "total_questions": 10,
            "estimated_time_minutes": 10
        },
        "questions": [
            {
                "question_id": "q1",
                "question_number": 1,
                "difficulty": "beginner",
                "topic": f"Introduction to {course_name}",
                "question_text": f"What is the primary focus of {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Solving real-world problems using the principles of " + course_name,
                    "B": "Memorizing facts about " + course_name,
                    "C": "Just theoretical knowledge",
                    "D": "None of the above"
                },
                "correct_answer": "A",
                "explanation": f"The main focus of {course_name} is practical application of core concepts.",
                "concept_tested": "Understanding Purpose"
            },
            {
                "question_id": "q2",
                "question_number": 2,
                "difficulty": "beginner",
                "topic": f"Basics of {course_name}",
                "question_text": f"Which of these is fundamental to {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Understanding core concepts",
                    "B": "Skipping practice",
                    "C": "Only memorizing",
                    "D": "Random guessing"
                },
                "correct_answer": "A",
                "explanation": "Understanding core concepts is essential for mastering any skill.",
                "concept_tested": "Core Knowledge"
            },
            {
                "question_id": "q3",
                "question_number": 3,
                "difficulty": "beginner",
                "topic": f"Fundamentals",
                "question_text": f"Why is practice important in learning {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "It helps reinforce learning and build skills",
                    "B": "It is not important",
                    "C": "Only for professionals",
                    "D": "It wastes time"
                },
                "correct_answer": "A",
                "explanation": "Regular practice is crucial for developing proficiency in any domain.",
                "concept_tested": "Learning Strategy"
            },
            {
                "question_id": "q4",
                "question_number": 4,
                "difficulty": "beginner",
                "topic": f"{course_name} Concepts",
                "question_text": f"What is a benefit of learning {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Improved problem-solving abilities",
                    "B": "No benefit",
                    "C": "Only for experts",
                    "D": "It is outdated"
                },
                "correct_answer": "A",
                "explanation": f"Learning {course_name} enhances analytical and practical skills.",
                "concept_tested": "Learning Benefits"
            },
            {
                "question_id": "q5",
                "question_number": 5,
                "difficulty": "intermediate",
                "topic": f"Applying {course_name}",
                "question_text": f"How would you apply {course_name} in a real-world scenario?",
                "code_snippet": "",
                "options": {
                    "A": "Use the concepts to solve practical problems",
                    "B": "Avoid practical application",
                    "C": "Only use theory",
                    "D": "It cannot be applied"
                },
                "correct_answer": "A",
                "explanation": f"Real-world application of {course_name} principles is essential for practical mastery.",
                "concept_tested": "Practical Application"
            },
            {
                "question_id": "q6",
                "question_number": 6,
                "difficulty": "intermediate",
                "topic": f"Advanced {course_name}",
                "question_text": f"What is an advanced technique in {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Combining multiple concepts for complex problem-solving",
                    "B": "Learning only basics",
                    "C": "Ignoring advanced topics",
                    "D": "Random approaches"
                },
                "correct_answer": "A",
                "explanation": "Advanced techniques involve integrating multiple concepts to solve complex problems.",
                "concept_tested": "Advanced Skills"
            },
            {
                "question_id": "q7",
                "question_number": 7,
                "difficulty": "intermediate",
                "topic": f"Best Practices",
                "question_text": f"What is a best practice when learning {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Consistent, structured learning with regular practice",
                    "B": "Random sporadic attempts",
                    "C": "Skipping fundamentals",
                    "D": "Learning without practice"
                },
                "correct_answer": "A",
                "explanation": "Consistency and structure are key to effective learning and skill development.",
                "concept_tested": "Learning Methodology"
            },
            {
                "question_id": "q8",
                "question_number": 8,
                "difficulty": "intermediate",
                "topic": f"Integration",
                "question_text": f"How does {course_name} integrate with other disciplines?",
                "code_snippet": "",
                "options": {
                    "A": "It complements and enhances skills in related areas",
                    "B": "It stands alone with no connections",
                    "C": "It contradicts other fields",
                    "D": "Integration is not possible"
                },
                "correct_answer": "A",
                "explanation": f"{course_name} often intersects with and strengthens capabilities in related domains.",
                "concept_tested": "Interdisciplinary Knowledge"
            },
            {
                "question_id": "q9",
                "question_number": 9,
                "difficulty": "advanced",
                "topic": f"Expert Level {course_name}",
                "question_text": f"What distinguishes an expert in {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Deep understanding, practical experience, and ability to solve complex problems",
                    "B": "Only theoretical knowledge",
                    "C": "Memorization of facts",
                    "D": "Quick guessing"
                },
                "correct_answer": "A",
                "explanation": "Expertise comes from deep knowledge, practical experience, and demonstrated problem-solving ability.",
                "concept_tested": "Expertise Definition"
            },
            {
                "question_id": "q10",
                "question_number": 10,
                "difficulty": "advanced",
                "topic": f"Mastery",
                "question_text": f"What is the path to mastery in {course_name}?",
                "code_snippet": "",
                "options": {
                    "A": "Continuous learning, deliberate practice, and application to real-world challenges",
                    "B": "Passive consumption of content",
                    "C": "One-time learning",
                    "D": "Avoiding challenges"
                },
                "correct_answer": "A",
                "explanation": "Mastery requires continuous improvement, deliberate practice, and tackling progressively harder challenges.",
                "concept_tested": "Path to Mastery"
            }
        ]
    }


def format_quiz_data(quiz_data, course_name):
    """Format LLM response into standard format"""
    if 'questions' not in quiz_data:
        return None
    
    # Pad with fallback if not enough questions
    fallback = generate_fallback_quiz(course_name)
    questions = quiz_data['questions']
    
    while len(questions) < 10:
        fallback_q = fallback['questions'][len(questions)]
        questions.append(fallback_q)
    
    questions = questions[:10]
    
    return {
        "quiz_metadata": {
            "course_name": course_name,
            "total_questions": 10,
            "estimated_time_minutes": 10
        },
        "questions": questions
    }


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
