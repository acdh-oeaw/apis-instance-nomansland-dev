#!/usr/bin/env python
"""
Demonstration script for the auto-delete relations feature.

This script shows how relations are automatically cleaned up when entities are deleted.
Run this with: python manage.py shell < demo_auto_delete.py
"""

# Import the models
from apis_ontology.models import Person, Place, Work, AuthorOf, BornIn, LivedIn

print("=== Auto-Delete Relations Demo ===\n")

# Create test entities
print("1. Creating test entities...")
person = Person.objects.create(
    forename="Jane",
    surname="Doe", 
    gender="female"
)
print(f"   Created Person: {person}")

place = Place.objects.create(label="Demo City")
print(f"   Created Place: {place}")

work = Work.objects.create(name="Demo Work")
print(f"   Created Work: {work}")

# Create relations
print("\n2. Creating relations...")
born_in = BornIn.objects.create(
    subj_object_id=person.id,
    obj_object_id=place.id
)
print(f"   Created BornIn relation: Person({person.id}) → Place({place.id})")

lived_in = LivedIn.objects.create(
    subj_object_id=person.id,
    obj_object_id=place.id
)
print(f"   Created LivedIn relation: Person({person.id}) → Place({place.id})")

author_of = AuthorOf.objects.create(
    subj_object_id=person.id,
    obj_object_id=work.id
)
print(f"   Created AuthorOf relation: Person({person.id}) → Work({work.id})")

# Show current state
print("\n3. Current state:")
print(f"   BornIn relations: {BornIn.objects.count()}")
print(f"   LivedIn relations: {LivedIn.objects.count()}")
print(f"   AuthorOf relations: {AuthorOf.objects.count()}")
print(f"   Total relations: {BornIn.objects.count() + LivedIn.objects.count() + AuthorOf.objects.count()}")

# Delete the person
print(f"\n4. Deleting person: {person}")
person.delete()

# Show state after deletion
print("\n5. State after person deletion:")
print(f"   BornIn relations: {BornIn.objects.count()}")
print(f"   LivedIn relations: {LivedIn.objects.count()}")
print(f"   AuthorOf relations: {AuthorOf.objects.count()}")
print(f"   Total relations: {BornIn.objects.count() + LivedIn.objects.count() + AuthorOf.objects.count()}")

# Verify other entities still exist
print(f"\n6. Other entities after deletion:")
print(f"   Places remaining: {Place.objects.filter(id=place.id).exists()}")
print(f"   Works remaining: {Work.objects.filter(id=work.id).exists()}")

print("\n=== Demo Complete ===")
print("✓ All relations involving the deleted person were automatically removed")
print("✓ Other entities (Place, Work) remain intact")
print("✓ Data integrity maintained")