import logging

logger = logging.getLogger(__name__)

def evaluate_assessment(assessment, user_answers, time_taken):
    """
    Comprehensive evaluation with scoring + analysis
    """
    
    quiz_data = assessment.quiz_data
    questions = quiz_data['questions']
    
    # Automatic scoring
    evaluation_results = {
        'overall_score': 0,
        'total_correct': 0,
        'total_questions': len(questions),
        'score_by_difficulty': {
            'beginner': {'correct': 0, 'total': 0},
            'intermediate': {'correct': 0, 'total': 0},
            'advanced': {'correct': 0, 'total': 0}
        },
        'topic_performance': {},
        'incorrect_questions': [],
        'time_analysis': {
            'total_seconds': time_taken,
            'avg_per_question': time_taken / len(questions) if len(questions) > 0 else 0,
            'pace': 'normal'
        }
    }
    
    # Score each question
    for question in questions:
        q_id = question['question_id']
        difficulty = question['difficulty']
        topic = question['topic']
        correct_answer = question['correct_answer']
        
        user_response = user_answers.get(q_id, {})
        user_answer = user_response.get('answer')
        
        is_correct = (user_answer == correct_answer)
        
        # Track by difficulty
        evaluation_results['score_by_difficulty'][difficulty]['total'] += 1
        if is_correct:
            evaluation_results['score_by_difficulty'][difficulty]['correct'] += 1
            evaluation_results['total_correct'] += 1
        
        # Track by topic
        if topic not in evaluation_results['topic_performance']:
            evaluation_results['topic_performance'][topic] = {
                'correct': 0,
                'total': 0,
                'proficiency_percent': 0
            }
        
        evaluation_results['topic_performance'][topic]['total'] += 1
        if is_correct:
            evaluation_results['topic_performance'][topic]['correct'] += 1
        
        # Track incorrect
        if not is_correct:
            evaluation_results['incorrect_questions'].append({
                'question_id': q_id,
                'question_number': question['question_number'],
                'topic': topic,
                'difficulty': difficulty,
                'user_answer': user_answer,
                'correct_answer': correct_answer,
                'explanation': question.get('explanation', '')
            })
    
    # Calculate percentages
    evaluation_results['overall_score'] = (
        evaluation_results['total_correct'] / evaluation_results['total_questions']
    ) * 100 if evaluation_results['total_questions'] > 0 else 0
    
    for topic, data in evaluation_results['topic_performance'].items():
        data['proficiency_percent'] = (data['correct'] / data['total']) * 100 if data['total'] > 0 else 0
    
    # Determine pace
    avg_time = evaluation_results['time_analysis']['avg_per_question']
    if avg_time < 40:
        evaluation_results['time_analysis']['pace'] = 'fast'
    elif avg_time > 90:
        evaluation_results['time_analysis']['pace'] = 'slow'
    
    # Generate learner profile with analysis (without LLM)
    learner_profile = generate_learner_profile_analysis(evaluation_results, assessment)
    evaluation_results['learner_profile'] = learner_profile
    
    return evaluation_results


def generate_learner_profile_analysis(eval_results, assessment):
    """
    Generate learner profile by analyzing results
    (No LLM call - pure Python analysis)
    """
    
    user = assessment.user
    overall_score = eval_results['overall_score']
    topic_perf = eval_results['topic_performance']
    difficulty_scores = eval_results['score_by_difficulty']
    
    # Determine skill level
    beginner_percent = (difficulty_scores['beginner']['correct'] / difficulty_scores['beginner']['total'] * 100) if difficulty_scores['beginner']['total'] > 0 else 0
    intermediate_percent = (difficulty_scores['intermediate']['correct'] / difficulty_scores['intermediate']['total'] * 100) if difficulty_scores['intermediate']['total'] > 0 else 0
    advanced_percent = (difficulty_scores['advanced']['correct'] / difficulty_scores['advanced']['total'] * 100) if difficulty_scores['advanced']['total'] > 0 else 0
    
    if overall_score < 40:
        skill_level = 'absolute_beginner'
        reasoning = f"Your score of {overall_score:.0f}% shows you are starting your learning journey. Focus on foundational concepts before moving to advanced topics."
    elif beginner_percent >= 80 and intermediate_percent < 50:
        skill_level = 'beginner'
        reasoning = f"You have solid grasp of basics ({beginner_percent:.0f}%) but need practice with intermediate concepts ({intermediate_percent:.0f}%). Keep building!"
    elif beginner_percent >= 80 and intermediate_percent >= 60:
        skill_level = 'intermediate'
        reasoning = f"You demonstrate strong fundamentals ({beginner_percent:.0f}%) and solid intermediate skills ({intermediate_percent:.0f}%). You're ready for more challenges!"
    else:
        skill_level = 'advanced'
        reasoning = f"Excellent performance across all levels. Your score of {overall_score:.0f}% shows strong mastery. Time for specialized topics!"
    
    # Identify strengths (topics with >70% score)
    strengths = []
    for topic, data in sorted(topic_perf.items(), key=lambda x: x[1]['proficiency_percent'], reverse=True):
        if data['proficiency_percent'] >= 70:
            strengths.append({
                'topic': topic,
                'proficiency_percent': int(data['proficiency_percent']),
                'note': f"You answered {data['correct']}/{data['total']} questions correctly"
            })
    
    if not strengths:
        strengths.append({
            'topic': 'Basic Concepts',
            'proficiency_percent': int(beginner_percent),
            'note': 'Your strongest area - foundation is solid'
        })
    
    # Identify weaknesses (topics with <60% score)
    weaknesses = []
    for topic, data in sorted(topic_perf.items(), key=lambda x: x[1]['proficiency_percent']):
        if data['proficiency_percent'] < 60:
            if data['proficiency_percent'] < 30:
                priority = 'high'
            elif data['proficiency_percent'] < 50:
                priority = 'medium'
            else:
                priority = 'low'
            
            weaknesses.append({
                'topic': topic,
                'proficiency_percent': int(data['proficiency_percent']),
                'note': f"Only {data['correct']}/{data['total']} correct - needs focused practice",
                'priority': priority
            })
    
    if not weaknesses:
        weaknesses.append({
            'topic': 'Advanced Topics',
            'proficiency_percent': int(advanced_percent),
            'note': 'Challenge yourself with more advanced problems',
            'priority': 'low'
        })
    
    # Estimate weeks to proficiency
    if overall_score >= 80:
        estimated_weeks = 2
    elif overall_score >= 60:
        estimated_weeks = 4
    elif overall_score >= 40:
        estimated_weeks = 6
    else:
        estimated_weeks = 8
    
    # Adjust based on user's weekly hours
    weekly_hours = assessment.user.profile.weekly_hours
    if weekly_hours <= 3:
        estimated_weeks = int(estimated_weeks * 1.5)
    elif weekly_hours >= 10:
        estimated_weeks = int(estimated_weeks * 0.7)
    
    # Generate next steps
    next_steps = generate_next_steps(skill_level, weaknesses, strengths)
    
    # Personalized message
    if overall_score >= 80:
        personal_msg = f"Fantastic! You scored {overall_score:.0f}%. You're making excellent progress! Keep up the momentum and tackle the next level."
    elif overall_score >= 60:
        personal_msg = f"Good work! You scored {overall_score:.0f}%. You have solid understanding. Focus on the weak areas to improve further."
    elif overall_score >= 40:
        personal_msg = f"You scored {overall_score:.0f}%. Don't worry - every expert was once a beginner. Review the concepts and try again!"
    else:
        personal_msg = f"Score: {overall_score:.0f}%. This is just the beginning of your learning journey. Take it step by step and you'll improve!"
    
    return {
        'skill_level': skill_level,
        'skill_level_reasoning': reasoning,
        'confidence_score': int(overall_score),
        'learning_pace': 'moderate',
        'strengths': strengths,
        'weaknesses': weaknesses,
        'recommended_starting_point': weaknesses[0]['topic'] if weaknesses else 'Advanced Topics',
        'prerequisites_needed': [],
        'estimated_weeks_to_proficiency': estimated_weeks,
        'personalized_message': personal_msg,
        'next_steps': next_steps
    }


def generate_next_steps(skill_level, weaknesses, strengths):
    """Generate personalized next steps based on skill level and performance"""
    
    steps = []
    
    # Add weakness-focused steps
    if weaknesses:
        weak_topic = weaknesses[0]['topic']
        steps.append(f"Master '{weak_topic}' - Your weakest area (focus here first)")
    
    # Add strength-building steps
    if strengths:
        strong_topic = strengths[0]['topic']
        steps.append(f"Build on '{strong_topic}' - Your strength (apply these skills to projects)")
    
    # Add skill level specific steps
    if skill_level == 'absolute_beginner':
        steps.append("Review fundamentals with simpler resources and examples")
        steps.append("Practice basic syntax and simple programs")
    elif skill_level == 'beginner':
        steps.append("Solve more intermediate-level problems")
        steps.append("Start building small projects to apply your knowledge")
    elif skill_level == 'intermediate':
        steps.append("Tackle advanced problems and edge cases")
        steps.append("Contribute to real-world projects or build your own")
    else:  # advanced
        steps.append("Explore specialized topics and advanced patterns")
        steps.append("Mentor others and build complex applications")
    
    # Add practice recommendation
    steps.append("Practice daily - consistency matters more than duration")
    
    return steps[:4]  # Return top 4 steps
