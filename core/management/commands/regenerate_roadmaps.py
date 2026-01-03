from django.core.management.base import BaseCommand
from core.models import SkillProfile


class Command(BaseCommand):
    help = 'Regenerate all roadmaps based on assessment results (skill level, weaknesses, strengths)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔄 Regenerating all roadmaps based on assessment results...'))
        
        from core.roadmap_generator import generate_learning_roadmap
        
        profiles = SkillProfile.objects.select_related('assessment', 'user').all()
        
        success_count = 0
        fail_count = 0
        
        for profile in profiles:
            try:
                # Extract topic
                topic = profile.assessment.custom_course_name or (
                    profile.assessment.course.title if profile.assessment.course else 'General'
                )
                
                # Get skill level from profile
                skill_level = profile.skill_level
                weaknesses = profile.weaknesses
                strengths = profile.strengths
                weekly_hours = profile.user.profile.weekly_hours if hasattr(profile.user, 'profile') else 5
                
                self.stdout.write(f'  🔨 Generating roadmap for {profile.user.username} - {topic} ({skill_level})...')
                
                # Generate new roadmap with correct skill level
                roadmap_data = generate_learning_roadmap(
                    topic=topic,
                    skill_level=skill_level,
                    weaknesses=weaknesses,
                    strengths=strengths,
                    weekly_hours=weekly_hours
                )
                
                if roadmap_data:
                    profile.roadmap_data = roadmap_data
                    profile.save()
                    success_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'    ✅ Generated {skill_level} level roadmap for {topic}'
                        )
                    )
                else:
                    fail_count += 1
                    self.stdout.write(
                        self.style.ERROR(
                            f'    ❌ Failed to generate roadmap for {topic}'
                        )
                    )
                    
            except Exception as e:
                fail_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'    ❌ Error for {profile.user.username}: {str(e)}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Regeneration complete!\n'
                f'   - Success: {success_count}\n'
                f'   - Failed: {fail_count}'
            )
        )
