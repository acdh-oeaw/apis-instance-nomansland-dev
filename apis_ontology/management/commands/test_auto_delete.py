from django.core.management.base import BaseCommand
from django.apps import apps
from apis_ontology.models import Person, Place, Work, AuthorOf, BornIn


class Command(BaseCommand):
    help = 'Test the auto-delete relations feature'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would happen without actually deleting',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Testing auto-delete relations feature...')
        )
        
        # Check if signal is properly connected
        from django.db.models.signals import post_delete
        from apis_ontology.signals import autodelete_relations
        
        # Find the signal handler
        receivers = post_delete._live_receivers(sender=Person)
        has_autodelete = any(
            receiver.__name__ == 'autodelete_relations' 
            for receiver in receivers
        )
        
        if has_autodelete:
            self.stdout.write(
                self.style.SUCCESS('✓ Auto-delete signal handler is connected')
            )
        else:
            self.stdout.write(
                self.style.ERROR('✗ Auto-delete signal handler is NOT connected')
            )
            return
            
        # Test with actual data if not dry run
        if not options['dry_run']:
            self.stdout.write('Creating test data...')
            
            # Create test entities
            person = Person.objects.create(
                forename="Test",
                surname="Person",
                gender="any"
            )
            place = Place.objects.create(label="Test Place")
            work = Work.objects.create(name="Test Work")
            
            # Create relations
            BornIn.objects.create(
                subj_object_id=person.id,
                obj_object_id=place.id
            )
            AuthorOf.objects.create(
                subj_object_id=person.id,
                obj_object_id=work.id
            )
            
            # Count relations before deletion
            born_in_count = BornIn.objects.filter(subj_object_id=person.id).count()
            author_of_count = AuthorOf.objects.filter(subj_object_id=person.id).count()
            total_before = born_in_count + author_of_count
            
            self.stdout.write(f'Relations before deletion: {total_before}')
            
            # Delete the person
            person_id = person.id
            person.delete()
            
            # Count relations after deletion
            born_in_after = BornIn.objects.filter(subj_object_id=person_id).count()
            author_of_after = AuthorOf.objects.filter(subj_object_id=person_id).count()
            total_after = born_in_after + author_of_after
            
            self.stdout.write(f'Relations after deletion: {total_after}')
            
            if total_after == 0:
                self.stdout.write(
                    self.style.SUCCESS('✓ Auto-delete working correctly!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('✗ Auto-delete failed - relations still exist')
                )
                
            # Cleanup
            Place.objects.filter(id=place.id).delete()
            Work.objects.filter(id=work.id).delete()
            
        else:
            self.stdout.write('Dry run mode - no actual testing performed')
            
        self.stdout.write(
            self.style.SUCCESS('Test complete.')
        )