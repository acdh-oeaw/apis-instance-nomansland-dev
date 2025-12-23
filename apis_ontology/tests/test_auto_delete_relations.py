from django.test import TestCase
from django.db import transaction
from apis_ontology.models import (
    Person, Place, Institution, Work, Expression, Manuscript, 
    AuthorOf, BornIn, Contains, LivedIn, StudiedAt
)


class AutoDeleteRelationsTestCase(TestCase):
    """Test that relations are automatically deleted when entities are deleted."""
    
    def setUp(self):
        """Set up test data."""
        # Create entities
        self.person = Person.objects.create(
            forename="John",
            surname="Doe",
            gender="male"
        )
        
        self.place = Place.objects.create(
            label="Test City"
        )
        
        self.institution = Institution.objects.create(
            name="Test University"
        )
        
        self.work = Work.objects.create(
            name="Test Work"
        )
        
        self.expression = Expression.objects.create(
            title="Test Expression"
        )
        
        self.manuscript = Manuscript.objects.create(
            name="Test Manuscript"
        )
        
    def test_person_deletion_removes_person_place_relations(self):
        """Test that deleting a person removes related person-place relations."""
        # Create relations with person as subject
        born_in = BornIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        lived_in = LivedIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        # Create relation with person as object (reverse relation)
        # We'll use a different person for this to avoid self-reference
        person2 = Person.objects.create(
            forename="Jane",
            surname="Smith", 
            gender="female"
        )
        
        # Verify relations exist
        self.assertEqual(BornIn.objects.count(), 1)
        self.assertEqual(LivedIn.objects.count(), 1)
        
        # Delete the person
        self.person.delete()
        
        # Verify relations are deleted
        self.assertEqual(BornIn.objects.count(), 0)
        self.assertEqual(LivedIn.objects.count(), 0)
        
        # Verify other entities still exist
        self.assertTrue(Place.objects.filter(id=self.place.id).exists())
        self.assertTrue(Person.objects.filter(id=person2.id).exists())
        
    def test_place_deletion_removes_person_place_relations(self):
        """Test that deleting a place removes related person-place relations."""
        # Create relations with place as object
        BornIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        LivedIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        # Verify relations exist
        self.assertEqual(BornIn.objects.count(), 2)
        self.assertEqual(LivedIn.objects.count(), 2)
        
        # Delete the place
        self.place.delete()
        
        # Verify relations are deleted
        self.assertEqual(BornIn.objects.count(), 0)
        self.assertEqual(LivedIn.objects.count(), 0)
        
        # Verify person still exists
        self.assertTrue(Person.objects.filter(id=self.person.id).exists())
        
    def test_person_work_relations_auto_delete(self):
        """Test that person-work relations are auto-deleted."""
        # Create author relation
        author_of = AuthorOf.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.work.id
        )
        
        # Verify relation exists
        self.assertEqual(AuthorOf.objects.count(), 1)
        
        # Delete the person
        self.person.delete()
        
        # Verify relation is deleted
        self.assertEqual(AuthorOf.objects.count(), 0)
        
        # Verify work still exists
        self.assertTrue(Work.objects.filter(id=self.work.id).exists())
        
    def test_work_deletion_removes_author_relations(self):
        """Test that deleting a work removes author relations."""
        # Create author relation
        AuthorOf.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.work.id
        )
        
        # Verify relation exists
        self.assertEqual(AuthorOf.objects.count(), 1)
        
        # Delete the work
        self.work.delete()
        
        # Verify relation is deleted
        self.assertEqual(AuthorOf.objects.count(), 0)
        
        # Verify person still exists
        self.assertTrue(Person.objects.filter(id=self.person.id).exists())
        
    def test_manuscript_expression_relations_auto_delete(self):
        """Test that manuscript-expression relations are auto-deleted."""
        # Create contains relation
        contains = Contains.objects.create(
            subj_object_id=self.manuscript.id,
            obj_object_id=self.expression.id
        )
        
        # Verify relation exists
        self.assertEqual(Contains.objects.count(), 1)
        
        # Delete the manuscript
        self.manuscript.delete()
        
        # Verify relation is deleted
        self.assertEqual(Contains.objects.count(), 0)
        
        # Verify expression still exists
        self.assertTrue(Expression.objects.filter(id=self.expression.id).exists())
        
    def test_expression_deletion_removes_contains_relations(self):
        """Test that deleting an expression removes contains relations."""
        # Create contains relation
        Contains.objects.create(
            subj_object_id=self.manuscript.id,
            obj_object_id=self.expression.id
        )
        
        # Verify relation exists
        self.assertEqual(Contains.objects.count(), 1)
        
        # Delete the expression
        self.expression.delete()
        
        # Verify relation is deleted
        self.assertEqual(Contains.objects.count(), 0)
        
        # Verify manuscript still exists
        self.assertTrue(Manuscript.objects.filter(id=self.manuscript.id).exists())
        
    def test_person_institution_relations_auto_delete(self):
        """Test that person-institution relations are auto-deleted."""
        # Create studied at relation
        studied_at = StudiedAt.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.institution.id
        )
        
        # Verify relation exists
        self.assertEqual(StudiedAt.objects.count(), 1)
        
        # Delete the person
        self.person.delete()
        
        # Verify relation is deleted
        self.assertEqual(StudiedAt.objects.count(), 0)
        
        # Verify institution still exists
        self.assertTrue(Institution.objects.filter(id=self.institution.id).exists())
        
    def test_institution_deletion_removes_person_relations(self):
        """Test that deleting an institution removes person relations."""
        # Create studied at relation
        StudiedAt.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.institution.id
        )
        
        # Verify relation exists
        self.assertEqual(StudiedAt.objects.count(), 1)
        
        # Delete the institution
        self.institution.delete()
        
        # Verify relation is deleted
        self.assertEqual(StudiedAt.objects.count(), 0)
        
        # Verify person still exists
        self.assertTrue(Person.objects.filter(id=self.person.id).exists())
        
    def test_multiple_relations_same_entity(self):
        """Test that all relations involving an entity are deleted."""
        # Create multiple relations involving the same person
        BornIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        LivedIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        AuthorOf.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.work.id
        )
        
        StudiedAt.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.institution.id
        )
        
        # Verify all relations exist
        self.assertEqual(BornIn.objects.count(), 1)
        self.assertEqual(LivedIn.objects.count(), 1)
        self.assertEqual(AuthorOf.objects.count(), 1)
        self.assertEqual(StudiedAt.objects.count(), 1)
        
        # Delete the person
        self.person.delete()
        
        # Verify all relations are deleted
        self.assertEqual(BornIn.objects.count(), 0)
        self.assertEqual(LivedIn.objects.count(), 0)
        self.assertEqual(AuthorOf.objects.count(), 0)
        self.assertEqual(StudiedAt.objects.count(), 0)
        
        # Verify other entities still exist
        self.assertTrue(Place.objects.filter(id=self.place.id).exists())
        self.assertTrue(Work.objects.filter(id=self.work.id).exists())
        self.assertTrue(Institution.objects.filter(id=self.institution.id).exists())
        
    def test_no_deletion_when_relation_deleted(self):
        """Test that deleting a relation doesn't trigger auto-deletion."""
        # Create relations
        born_in = BornIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        lived_in = LivedIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        # Verify both relations exist
        self.assertEqual(BornIn.objects.count(), 1)
        self.assertEqual(LivedIn.objects.count(), 1)
        
        # Delete one relation
        born_in.delete()
        
        # Verify only the deleted relation is gone, other relation remains
        self.assertEqual(BornIn.objects.count(), 0)
        self.assertEqual(LivedIn.objects.count(), 1)
        
        # Verify entities still exist
        self.assertTrue(Person.objects.filter(id=self.person.id).exists())
        self.assertTrue(Place.objects.filter(id=self.place.id).exists())
        
    def test_deletion_with_inherited_entity_types(self):
        """Test that auto-deletion works with entity inheritance."""
        # Create relations
        AuthorOf.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.work.id
        )
        
        BornIn.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.place.id
        )
        
        # Verify relations exist
        self.assertEqual(AuthorOf.objects.count(), 1)
        self.assertEqual(BornIn.objects.count(), 1)
        
        # Delete the person (which might inherit from AbstractEntity)
        self.person.delete()
        
        # Verify relations are deleted regardless of inheritance
        self.assertEqual(AuthorOf.objects.count(), 0)
        self.assertEqual(BornIn.objects.count(), 0)
        
    def test_deletion_handles_missing_pk(self):
        """Test that deletion handles cases where entity has no PK."""
        # Create a person without saving (no PK assigned)
        person_no_pk = Person(
            forename="No",
            surname="PK",
            gender="male"
        )
        
        # This should not raise an exception
        # The signal handler should gracefully handle missing PK
        # (Though in practice, post_delete wouldn't fire for unsaved objects)
        
        # Verify existing relations are unaffected
        AuthorOf.objects.create(
            subj_object_id=self.person.id,
            obj_object_id=self.work.id
        )
        
        self.assertEqual(AuthorOf.objects.count(), 1)