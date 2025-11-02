from django.core.management.base import BaseCommand
from core.models import Course


class Command(BaseCommand):
    help = 'Seed database with initial course data'

    def handle(self, *args, **options):
        courses = [
            {
                'course_id': 'python_basics',
                'title': 'Python Programming',
                'description': 'Learn Python from fundamentals to intermediate concepts. Build real projects and master programming fundamentals.',
                'icon_emoji': '🐍',
                'difficulty_range': 'Beginner to Intermediate',
                'estimated_weeks_min': 6,
                'estimated_weeks_max': 8,
                'topics_covered': [
                    'Variables & Data Types',
                    'Control Flow (if/else, loops)',
                    'Functions',
                    'Lists & Dictionaries',
                    'File Handling',
                    'Object-Oriented Programming Basics',
                    'Error Handling',
                    'Common Modules (os, sys, datetime)',
                    'List Comprehensions'
                ],
                'prerequisites': [],
                'learning_outcomes': [
                    'Write Python scripts for automation',
                    'Build command-line applications',
                    'Understand OOP fundamentals',
                    'Debug and test Python code',
                    'Work with files and data structures'
                ],
                'is_available': True
            },
            {
                'course_id': 'javascript_basics',
                'title': 'JavaScript Fundamentals',
                'description': 'Master modern JavaScript, DOM manipulation, and ES6+ features for web development.',
                'icon_emoji': '⚡',
                'difficulty_range': 'Beginner',
                'estimated_weeks_min': 6,
                'estimated_weeks_max': 8,
                'topics_covered': [
                    'Variables & Data Types',
                    'Functions & Arrow Functions',
                    'DOM Manipulation',
                    'Events',
                    'Async/Await',
                    'Promises',
                    'ES6+ Features'
                ],
                'prerequisites': [],
                'learning_outcomes': [
                    'Build interactive web applications',
                    'Manipulate the DOM effectively',
                    'Handle asynchronous operations',
                    'Write clean, modern JavaScript'
                ],
                'is_available': False
            }
        ]

        for course_data in courses:
            course, created = Course.objects.get_or_create(
                course_id=course_data['course_id'],
                defaults=course_data
            )
            
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created course: {course.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Course already exists: {course.title}')
                )

        self.stdout.write(
            self.style.SUCCESS('Course seeding completed successfully!')
        )
