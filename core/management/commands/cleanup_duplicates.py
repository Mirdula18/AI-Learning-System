from django.core.management.base import BaseCommand
from django.db.models import Count
from core.models import Assessment, SkillProfile


class Command(BaseCommand):
    help = 'Remove duplicate assessments for the same course (keep only the first one)'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('🔍 Searching for duplicate assessments...'))
        
        deleted_count = 0
        kept_count = 0
        
        # Find all users with their courses
        assessments = Assessment.objects.filter(status='completed').order_by('user', 'custom_course_name', 'completed_at')
        
        seen = {}  # Track (user_id, course_name) combinations
        to_delete = []
        
        for assessment in assessments:
            key = (assessment.user_id, assessment.custom_course_name)
            
            if key in seen:
                # This is a duplicate - mark for deletion
                to_delete.append(assessment.id)
                self.stdout.write(
                    self.style.ERROR(
                        f'  ❌ Duplicate: User {assessment.user.username} - '
                        f'{assessment.custom_course_name} (ID: {assessment.id})'
                    )
                )
            else:
                # This is the first one - keep it
                seen[key] = assessment.id
                kept_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'  ✅ Keeping: User {assessment.user.username} - '
                        f'{assessment.custom_course_name} (ID: {assessment.id})'
                    )
                )
        
        if to_delete:
            self.stdout.write(self.style.WARNING(f'\n📝 Found {len(to_delete)} duplicate assessments to remove'))
            self.stdout.write('Deleting associated SkillProfiles...')
            
            # Delete associated SkillProfiles first
            SkillProfile.objects.filter(assessment_id__in=to_delete).delete()
            
            # Delete the duplicate assessments
            deleted_count = Assessment.objects.filter(id__in=to_delete).delete()[0]
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✅ Cleanup complete!\n'
                    f'   - Kept: {kept_count} assessments\n'
                    f'   - Deleted: {deleted_count} duplicate assessments'
                )
            )
        else:
            self.stdout.write(self.style.SUCCESS('\n✅ No duplicates found! Database is clean.'))
