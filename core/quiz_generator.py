import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_assessment_quiz(course, user):
    """
    Generate personalized quiz using Gemini API
    """
    
    # Simple hardcoded quiz for now (fallback)
    fallback_quiz = {
        "quiz_metadata": {
            "course_id": course.course_id,
            "total_questions": 10,
            "estimated_time_minutes": 15
        },
        "questions": [
            {"question_id": "q1", "question_number": 1, "difficulty": "beginner", "topic": "Variables & Data Types", "question_text": "What does the print() function do in Python?", "code_snippet": "print('Hello')", "options": {"A": "Displays output to console", "B": "Stores data", "C": "Creates a variable", "D": "Deletes data"}, "correct_answer": "A", "explanation": "print() outputs text to the screen.", "concept_tested": "Basic I/O"},
            {"question_id": "q2", "question_number": 2, "difficulty": "beginner", "topic": "Variables & Data Types", "question_text": "What is the output of: print(2 + 3)?", "code_snippet": "print(2 + 3)", "options": {"A": "5", "B": "23", "C": "2 + 3", "D": "Error"}, "correct_answer": "A", "explanation": "2 + 3 equals 5", "concept_tested": "Arithmetic operations"},
            {"question_id": "q3", "question_number": 3, "difficulty": "beginner", "topic": "Variables & Data Types", "question_text": "What is a variable?", "code_snippet": "x = 10", "options": {"A": "A container to store data", "B": "A function", "C": "A library", "D": "A syntax error"}, "correct_answer": "A", "explanation": "Variables store values in memory.", "concept_tested": "Variable concept"},
            {"question_id": "q4", "question_number": 4, "difficulty": "beginner", "topic": "Control Flow", "question_text": "What does an if statement do?", "code_snippet": "if x > 5:\n    print('Big')", "options": {"A": "Executes code conditionally", "B": "Loops forever", "C": "Defines a function", "D": "Creates a variable"}, "correct_answer": "A", "explanation": "if statements execute code only when conditions are true.", "concept_tested": "Conditional logic"},
            {"question_id": "q5", "question_number": 5, "difficulty": "beginner", "topic": "Control Flow", "question_text": "What will print: x = 3; if x < 5: print('yes')", "code_snippet": "x = 3\nif x < 5:\n    print('yes')", "options": {"A": "yes", "B": "no", "C": "Error", "D": "Nothing"}, "correct_answer": "A", "explanation": "3 < 5 is true, so 'yes' prints.", "concept_tested": "If statement evaluation"},
            {"question_id": "q6", "question_number": 6, "difficulty": "intermediate", "topic": "Lists & Dictionaries", "question_text": "What is a list in Python?", "code_snippet": "my_list = [1, 2, 3]", "options": {"A": "An ordered collection of items", "B": "A single value", "C": "A function", "D": "A string"}, "correct_answer": "A", "explanation": "Lists store multiple items in order.", "concept_tested": "List concept"},
            {"question_id": "q7", "question_number": 7, "difficulty": "intermediate", "topic": "Lists & Dictionaries", "question_text": "How do you access the first item in a list?", "code_snippet": "my_list = ['a', 'b', 'c']\nprint(my_list[0])", "options": {"A": "my_list[0]", "B": "my_list[1]", "C": "my_list.first()", "D": "my_list.get(0)"}, "correct_answer": "A", "explanation": "Python uses 0-based indexing.", "concept_tested": "List indexing"},
            {"question_id": "q8", "question_number": 8, "difficulty": "intermediate", "topic": "Functions", "question_text": "What is a function?", "code_snippet": "def greet():\n    print('Hello')", "options": {"A": "A reusable block of code", "B": "A variable", "C": "A data type", "D": "A loop"}, "correct_answer": "A", "explanation": "Functions encapsulate reusable code.", "concept_tested": "Function concept"},
            {"question_id": "q9", "question_number": 9, "difficulty": "intermediate", "topic": "Functions", "question_text": "What does 'return' do in a function?", "code_snippet": "def add(a, b):\n    return a + b", "options": {"A": "Sends a value back to caller", "B": "Prints output", "C": "Ends the program", "D": "Stores a variable"}, "correct_answer": "A", "explanation": "return sends values back from functions.", "concept_tested": "Return statements"},
            {"question_id": "q10", "question_number": 10, "difficulty": "intermediate", "topic": "Loops", "question_text": "What does a for loop do?", "code_snippet": "for i in range(3):\n    print(i)", "options": {"A": "Repeats code multiple times", "B": "Makes decisions", "C": "Stores data", "D": "Creates a function"}, "correct_answer": "A", "explanation": "for loops iterate over sequences.", "concept_tested": "Loop concept"},
            {"question_id": "q11", "question_number": 11, "difficulty": "intermediate", "topic": "Loops", "question_text": "What is the output: for i in range(3): print(i)", "code_snippet": "for i in range(3):\n    print(i)", "options": {"A": "0 1 2", "B": "1 2 3", "C": "0 1 2 3", "D": "Error"}, "correct_answer": "A", "explanation": "range(3) produces 0, 1, 2", "concept_tested": "range() function"},
            {"question_id": "q12", "question_number": 12, "difficulty": "intermediate", "topic": "Error Handling", "question_text": "What is try-except used for?", "code_snippet": "try:\n    x = 1/0\nexcept:\n    print('Error')", "options": {"A": "Catches and handles errors", "B": "Defines a function", "C": "Creates a loop", "D": "Stores variables"}, "correct_answer": "A", "explanation": "try-except handles runtime errors gracefully.", "concept_tested": "Error handling"},
            {"question_id": "q13", "question_number": 13, "difficulty": "advanced", "topic": "OOP Basics", "question_text": "What is a class?", "code_snippet": "class Dog:\n    def __init__(self, name):\n        self.name = name", "options": {"A": "A blueprint for objects", "B": "A function", "C": "A list", "D": "A string"}, "correct_answer": "A", "explanation": "Classes define object blueprints.", "concept_tested": "Class concept"},
            {"question_id": "q14", "question_number": 14, "difficulty": "advanced", "topic": "OOP Basics", "question_text": "What is an object?", "code_snippet": "dog = Dog('Buddy')", "options": {"A": "An instance of a class", "B": "A data type", "C": "A function", "D": "A variable name"}, "correct_answer": "A", "explanation": "Objects are instances created from classes.", "concept_tested": "Object concept"},
            {"question_id": "q15", "question_number": 15, "difficulty": "advanced", "topic": "Advanced Python", "question_text": "What is list comprehension?", "code_snippet": "squares = [x**2 for x in range(5)]", "options": {"A": "Concise way to create lists", "B": "A loop statement", "C": "Error syntax", "D": "A function"}, "correct_answer": "A", "explanation": "List comprehension creates lists efficiently.", "concept_tested": "List comprehension"},
        ]
    }
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Generate 15 Python quiz questions in JSON format")
        
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
            logger.info(f"Quiz generated successfully for {course.title}")
            return quiz_data
        else:
            logger.warning("Generated quiz validation failed, using fallback")
            return fallback_quiz
            
    except Exception as e:
        logger.error(f"Quiz generation failed: {str(e)}, using fallback")
        return fallback_quiz


def validate_quiz_structure(quiz_data):
    """Validate generated quiz meets requirements"""
    
    try:
        if 'quiz_metadata' not in quiz_data or 'questions' not in quiz_data:
            return False
        
        questions = quiz_data['questions']
        
        if len(questions) != 15:
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
