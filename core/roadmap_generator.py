import google.generativeai as genai
from django.conf import settings
import json
import logging

logger = logging.getLogger(__name__)

genai.configure(api_key=settings.GEMINI_API_KEY)

def generate_learning_roadmap(topic, skill_level, weaknesses, strengths, weekly_hours):
    """Generate a personalized 12-week learning roadmap"""
    
    # Try LLM first
    roadmap = try_llm_roadmap(topic, skill_level, weaknesses, strengths, weekly_hours)
    
    # Fallback to structured roadmap
    if not roadmap:
        logger.warning(f"LLM roadmap failed for {topic}, using structured fallback")
        roadmap = generate_structured_roadmap(topic, skill_level, weaknesses, strengths, weekly_hours)
    
    return roadmap


def try_llm_roadmap(topic, skill_level, weaknesses, strengths, weekly_hours):
    """Try to generate roadmap using LLM"""
    try:
        weak_topics = ', '.join([w['topic'] for w in weaknesses[:3]]) if weaknesses else 'None'
        strong_topics = ', '.join([s['topic'] for s in strengths[:2]]) if strengths else 'None'
        
        prompt = """Create a detailed 12-week personalized learning roadmap for """ + topic + """.

Student Profile:
- Current Level: """ + skill_level + """
- Strengths: """ + strong_topics + """
- Weaknesses: """ + weak_topics + """
- Available: """ + str(weekly_hours) + """ hours/week

Return ONLY valid JSON in this format:
{
  "weeks": [
    {
      "week": 1,
      "title": "Week Title",
      "focus_areas": ["Area 1", "Area 2"],
      "learning_objectives": ["Learn X", "Understand Y"],
      "resources": [
        {"type": "video", "title": "Title", "description": "Description", "time_estimate": "2 hours"}
      ],
      "practice_exercises": ["Exercise 1", "Exercise 2"],
      "daily_tasks": ["Monday: Do X", "Tuesday: Do Y"],
      "milestone": "What you should achieve",
      "estimated_hours": 5
    }
  ],
  "milestones": [
    {"week": 3, "title": "Title", "description": "Description"}
  ],
  "success_tips": ["Tip 1", "Tip 2"],
  "project_ideas": [
    {"week": 4, "title": "Project", "description": "Build X", "complexity": "beginner", "duration": "3 days"}
  ]
}"""
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        
        # Clean response
        if '```':
            response_text = response_text.split('```')[1]
            if response_text.startswith('json'):
                response_text = response_text[4:]
        
        response_text = response_text.strip()
        roadmap_data = json.loads(response_text)
        
        # Validate
        if 'weeks' in roadmap_data and len(roadmap_data['weeks']) >= 10:
            logger.info(f"LLM roadmap generated for: {topic}")
            return format_roadmap_response(roadmap_data, topic, skill_level, weekly_hours)
        
        return None
    except Exception as e:
        logger.error(f"LLM roadmap failed: {str(e)}")
        return None


def generate_structured_roadmap(topic, skill_level, weaknesses, strengths, weekly_hours):
    """Generate structured fallback roadmap"""
    
    # Determine weeks needed based on skill level
    weeks_needed = {
        'absolute_beginner': 12,
        'beginner': 10,
        'intermediate': 6,
        'advanced': 4
    }
    
    total_weeks = weeks_needed.get(skill_level, 8)
    
    weeks = []
    
    # Week 1: Assessment & Foundation
    weeks.append({
        "week": 1,
        "title": " Start Your Journey",
        "tagline": "Foundation & Getting Started",
        "focus_areas": [f"Introduction to {topic}", "Key Terminology", "Basic Principles"],
        "weak_focus": True if weaknesses else False,
        "learning_objectives": [
            f"Understand what {topic} is",
            f"Learn core principles of {topic}",
            "Grasp essential terminology"
        ],
        "resources": [
            {
                "type": "tutorial",
                "title": f"Getting Started with {topic}",
                "description": f"Comprehensive introduction to {topic} fundamentals",
                "time_estimate": "3 hours"
            },
            {
                "type": "reading",
                "title": f"{topic} Basics Guide",
                "description": "Essential reading material for beginners",
                "time_estimate": "2 hours"
            }
        ],
        "practice_exercises": [
            "Complete vocabulary quiz",
            "Identify core concepts in examples",
            "Answer 20 practice questions"
        ],
        "daily_tasks": [
            " Monday-Tuesday: Watch introductory videos (3 hrs)",
            " Wednesday: Read foundational material (2 hrs)",
            " Thursday-Friday: Complete practice exercises (3 hrs)",
            " Weekend: Consolidate learning, create summary notes (3 hrs)"
        ],
        "milestone": "Understand basic concepts and vocabulary",
        "estimated_hours": weekly_hours,
        "motivation": "Every expert was once a beginner. You're taking the first step!"
    })
    
    # Weeks 2-N: Based on weak areas
    if total_weeks >= 2:
        weak_topics = [w['topic'] for w in weaknesses[:2]] if weaknesses else []
        weak_description = f"Focus on {', '.join(weak_topics)}" if weak_topics else "Strengthen core concepts"
        
        weeks.append({
            "week": 2,
            "title": " Deep Dive Into Concepts",
            "tagline": weak_description,
            "focus_areas": weak_topics or [f"{topic} Core Concepts"],
            "weak_focus": True,
            "learning_objectives": [
                f"Master {weak_topics[0] if weak_topics else 'fundamental'} concepts",
                "Build a strong conceptual foundation",
                "Understand practical applications"
            ],
            "resources": [
                {
                    "type": "course",
                    "title": f"Understanding {topic} Principles",
                    "description": "In-depth exploration of core concepts",
                    "time_estimate": "4 hours"
                }
            ],
            "practice_exercises": [
                f"Master {weak_topics[0] if weak_topics else 'core'} through 30 problems",
                "Explain concepts in your own words",
                "Solve real-world scenarios"
            ],
            "daily_tasks": [
                " Monday-Tuesday: Study core principles (4 hrs)",
                " Wednesday: Review practical examples (2 hrs)",
                " Thursday-Friday: Practice concept mapping (3 hrs)",
                " Weekend: Create concept summary cards (3 hrs)"
            ],
            "milestone": "Deep understanding of core concepts",
            "estimated_hours": weekly_hours,
            "motivation": "You're building a solid foundation. Keep going! "
        })
    
    if total_weeks >= 3:
        weeks.append({
            "week": 3,
            "title": " Hands-On Practice",
            "tagline": "Build Your First Real Project",
            "focus_areas": ["Practical Application", "Problem Solving", "Project Building"],
            "weak_focus": False,
            "learning_objectives": [
                "Apply concepts to solve real problems",
                "Build your first practical project",
                "Understand common mistakes"
            ],
            "resources": [
                {
                    "type": "project",
                    "title": f"Build Your First {topic} Project",
                    "description": "Simple beginner-friendly project",
                    "time_estimate": "5 hours"
                }
            ],
            "practice_exercises": [
                "Solve 20 practical problems",
                "Build and complete mini-project",
                "Debug and optimize your solution"
            ],
            "daily_tasks": [
                " Monday-Wednesday: Build mini-project (6 hrs)",
                " Thursday: Test and debug (2 hrs)",
                " Friday: Optimize and improve (2 hrs)",
                " Weekend: Document and reflect (2 hrs)"
            ],
            "milestone": "Complete first practical project",
            "estimated_hours": weekly_hours,
            "motivation": "You built something! That's a huge milestone "
        })
    
    if total_weeks >= 4:
        weeks.append({
            "week": 4,
            "title": " Level Up",
            "tagline": "Intermediate Techniques & Patterns",
            "focus_areas": ["Advanced Concepts", "Best Practices", "Optimization"],
            "weak_focus": False,
            "learning_objectives": [
                "Learn intermediate techniques",
                "Understand design patterns",
                "Follow industry best practices"
            ],
            "resources": [
                {
                    "type": "course",
                    "title": f"Advanced {topic} Techniques",
                    "description": "Intermediate level deep dive",
                    "time_estimate": "4 hours"
                }
            ],
            "practice_exercises": [
                "Solve 25 intermediate problems",
                "Implement 3 different approaches",
                "Optimize existing solutions"
            ],
            "daily_tasks": [
                " Monday-Tuesday: Study advanced techniques (4 hrs)",
                " Wednesday-Thursday: Implement and practice (4 hrs)",
                " Friday: Optimize solutions (2 hrs)",
                " Weekend: Study best practices (2 hrs)"
            ],
            "milestone": "Master intermediate techniques",
            "estimated_hours": weekly_hours,
            "motivation": "You're becoming proficient! The best is yet to come "
        })
    
    if total_weeks >= 5:
        weeks.append({
            "week": 5,
            "title": " Build Bigger",
            "tagline": "Complex Project Integration",
            "focus_areas": ["System Design", "Integration", "Problem Solving"],
            "weak_focus": False,
            "learning_objectives": [
                "Build more complex projects",
                "Integrate multiple concepts",
                "Apply strategic thinking"
            ],
            "resources": [
                {
                    "type": "project",
                    "title": f"Build Medium-Complexity {topic} Project",
                    "description": "Intermediate project combining skills",
                    "time_estimate": "8 hours"
                }
            ],
            "practice_exercises": [
                "Plan and design architecture",
                "Implement core features",
                "Add advanced features",
                "Test thoroughly"
            ],
            "daily_tasks": [
                " Monday: Plan and design (2 hrs)",
                " Tuesday-Thursday: Implement features (6 hrs)",
                " Friday: Add advanced features (2 hrs)",
                " Weekend: Test and document (2 hrs)"
            ],
            "milestone": "Complete medium complexity project",
            "estimated_hours": weekly_hours,
            "motivation": "Projects speak louder than words! You're building a portfolio "
        })
    
    if total_weeks >= 6:
        weeks.append({
            "week": 6,
            "title": " Master Achiever",
            "tagline": "Final Push to Proficiency",
            "focus_areas": ["Mastery", "Optimization", "Real-World Skills"],
            "weak_focus": False,
            "learning_objectives": [
                "Achieve proficiency level mastery",
                "Optimize for production",
                "Apply real-world scenarios"
            ],
            "resources": [
                {
                    "type": "course",
                    "title": f"Professional {topic} Practices",
                    "description": "Production-ready techniques",
                    "time_estimate": "4 hours"
                }
            ],
            "practice_exercises": [
                "Solve advanced real-world problems",
                "Build optimized solutions",
                "Create production-ready code"
            ],
            "daily_tasks": [
                " Monday-Tuesday: Study professional practices (4 hrs)",
                " Wednesday-Thursday: Build production-ready solution (4 hrs)",
                " Friday: Polish and optimize (2 hrs)",
                " Weekend: Celebrate and reflect (2 hrs)"
            ],
            "milestone": "Achieve proficiency and professional readiness",
            "estimated_hours": weekly_hours,
            "motivation": "You've reached your goal! From beginner to proficient "
        })
    
    # Create motivational message
    motivation_message = get_motivation_message(skill_level, len(weaknesses), total_weeks)
    
    # Success tips focused on weak areas
    success_tips = get_personalized_tips(skill_level, weaknesses, total_weeks)
    
    return {
        "roadmap_title": f"Your {total_weeks}-Week Journey to {topic} Proficiency",
        "overview": motivation_message,
        "total_weeks": total_weeks,
        "weekly_hours_required": weekly_hours,
        "skill_level": skill_level,
        "focus_areas": [w['topic'] for w in weaknesses[:3]] if weaknesses else [],
        "weeks": weeks[:total_weeks],
        "milestones": get_milestones(total_weeks),
        "success_tips": success_tips,
        "project_ideas": get_project_ideas_focused(topic, total_weeks, weaknesses)
    }


def get_motivation_message(skill_level, weak_count, weeks):
    """Create personalized motivation message"""
    messages = {
        'absolute_beginner': f" Welcome to your learning journey! You're starting from scratch, and that's awesome. In just {weeks} weeks of {5} hours per week, you'll transform from a complete beginner to a proficient professional. This roadmap is tailored to your unique learning needs. Let's do this! ",
        'beginner': f" Great! You have some foundation. In {weeks} weeks, we'll strengthen your weak areas and take your skills to the next level. You're on the right track! ",
        'intermediate': f" You're already solid! In {weeks} weeks of focused practice on your weaker areas, you'll achieve true proficiency. Time to master the details! ",
        'advanced': f" You're almost there! Just {weeks} more weeks to cross the finish line to mastery. Let's polish your weak spots and reach the summit! "
    }
    return messages.get(skill_level, "Let's start this amazing journey! ")


def get_personalized_tips(skill_level, weaknesses, weeks):
    """Generate personalized success tips based on weak areas"""
    tips = []
    
    # Motivational tip
    tips.append(" You've got this! Progress > Perfection. Small steps daily lead to big achievements.")
    tips.append(" Consistency is key. Show up every day, even if just for 30 minutes.")
    
    if weaknesses:
        weak_topics = [w['topic'] for w in weaknesses[:2]]
        tips.append(f"🎓 Extra focus on {weak_topics[0]}: This is your superpower to unlock!")
    
    tips.extend([
        " Build projects! Nothing beats learning by doing.",
        " Connect with others learning the same topic - share, learn, grow together.",
        " Keep a learning journal - track what you learn and celebrate wins.",
        " Review regularly - spaced repetition is your secret weapon.",
        " Don't compare your beginning to someone else's middle.",
        f" In {weeks} weeks, you'll be amazed at how far you've come!"
    ])
    
    return tips[:8]


def get_milestones(total_weeks):
    """Generate milestone checkpoints"""
    milestones = []
    
    if total_weeks >= 2:
        milestones.append({
            "week": 1,
            "title": " Journey Begins",
            "description": "Foundation laid, concepts understood"
        })
    
    if total_weeks >= 3:
        milestones.append({
            "week": 2,
            "title": " Building Momentum",
            "description": "Weak areas strengthened, confidence growing"
        })
    
    if total_weeks >= 4:
        milestones.append({
            "week": 3,
            "title": " First Victory",
            "description": "First project completed! Proof of progress"
        })
    
    if total_weeks >= 6:
        milestones.append({
            "week": total_weeks,
            "title": " Proficiency Achieved",
            "description": "You're now proficient! Ready for real-world challenges"
        })
    
    return milestones


def get_project_ideas_focused(topic, total_weeks, weaknesses):
    """Generate project ideas focused on weak areas"""
    weak_area = weaknesses[0]['topic'] if weaknesses else None
    
    projects = [
        {
            "week": 1,
            "title": f" Master {weak_area or 'Your Weak Area'}",
            "description": f"Focused exercises to strengthen {weak_area or 'areas you are struggling with'}",
            "complexity": "beginner",
            "duration": "Daily practice",
            "focus": "weak" if weak_area else "foundation"
        }
    ]
    
    if total_weeks >= 2:
        projects.append({
            "week": 2,
            "title": f" Apply {weak_area or 'Core Concepts'}",
            "description": f"Build something using what you just learned about {weak_area or 'core concepts'}",
            "complexity": "beginner",
            "duration": "2-3 days",
            "focus": "application"
        })
    
    if total_weeks >= 3:
        projects.append({
            "week": 3,
            "title": f" Complete Your First {topic} Project",
            "description": "A complete project combining all learned concepts",
            "complexity": "intermediate",
            "duration": "Full week",
            "focus": "integration"
        })
    
    if total_weeks >= 5:
        projects.append({
            "week": 5,
            "title": f" Advanced {topic} Project",
            "description": "Push yourself with a more complex project",
            "complexity": "advanced",
            "duration": "2 weeks",
            "focus": "mastery"
        })
    
    return projects


def get_success_tips(skill_level, topic, weaknesses):
    """Generate personalized success tips"""
    tips = [
        f"Consistent practice with {weekly_hours} hours per week is more effective than cramming",
        "Build projects as you learn - theory + practice combination is powerful",
        "Join communities to get feedback and learn from others",
        "Break down complex topics into smaller, manageable chunks",
        "Review and consolidate learning regularly (spaced repetition)",
        "Keep a learning journal to track progress and insights"
    ]
    
    if skill_level == 'absolute_beginner':
        tips.extend([
            "Don't rush - it's normal to need time to grasp concepts",
            "Use multiple learning resources - videos, books, courses",
            "Practice debugging by fixing intentional errors in code"
        ])
    elif skill_level == 'intermediate':
        tips.extend([
            "Focus on design patterns and best practices",
            "Contribute to open-source projects for real-world experience",
            "Learn from reading others' code"
        ])
    else:
        tips.extend([
            "Mentor others to deepen your own understanding",
            "Stay updated with latest developments in the field",
            "Focus on innovation and unique solutions"
        ])
    
    if weaknesses:
        weak_area = weaknesses[0]['topic'] if weaknesses else None
        if weak_area:
            tips.append(f"Dedicate extra time to strengthening your {weak_area} skills")
    
    return tips[:8]  # Return top 8 tips


def get_project_ideas(topic, skill_level, weekly_hours):
    """Generate personalized project ideas"""
    projects = [
        {
            "week": 3,
            "title": f"Build Basic {topic} Project",
            "description": f"Create a simple project to apply Week 1-2 concepts",
            "complexity": "beginner",
            "duration": "3 days",
            "skills": "Core concepts application"
        },
        {
            "week": 5,
            "title": f"Medium {topic} Application",
            "description": f"Develop an application combining multiple {topic} concepts",
            "complexity": "intermediate",
            "duration": "1 week",
            "skills": "Integration, problem-solving"
        },
        {
            "week": 8,
            "title": f"Advanced {topic} System",
            "description": f"Design and build a complex, scalable {topic} system",
            "complexity": "advanced",
            "duration": "2 weeks",
            "skills": "Architecture, optimization, testing"
        },
        {
            "week": 11,
            "title": f"Capstone: Professional {topic} Project",
            "description": f"Your masterpiece - a production-ready {topic} project",
            "complexity": "expert",
            "duration": "3 weeks",
            "skills": "All learned concepts, professionalism"
        }
    ]
    
    return projects


def format_roadmap_response(roadmap_data, topic, skill_level, weekly_hours):
    """Format LLM response into standard format"""
    if 'weeks' not in roadmap_data or len(roadmap_data['weeks']) < 10:
        # Fallback if LLM response incomplete
        return generate_structured_roadmap(topic, skill_level, [], [], weekly_hours)
    
    # Add missing fields if needed
    if 'milestones' not in roadmap_data:
        roadmap_data['milestones'] = []
    
    if 'success_tips' not in roadmap_data:
        roadmap_data['success_tips'] = []
    
    if 'project_ideas' not in roadmap_data:
        roadmap_data['project_ideas'] = []
    
    return {
        "roadmap_title": f"Your 12-Week {topic} Mastery Roadmap",
        "overview": f"A comprehensive personalized learning path to master {topic}",
        "total_weeks": 12,
        "weekly_hours_required": weekly_hours,
        "skill_level": skill_level,
        "weeks": roadmap_data['weeks'][:12],
        "milestones": roadmap_data.get('milestones', []),
        "success_tips": roadmap_data.get('success_tips', []),
        "project_ideas": roadmap_data.get('project_ideas', [])
    }
