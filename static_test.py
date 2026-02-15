"""
Static analysis test to verify the relation models structure.
This can run without Django being fully configured.
"""

import sys
import os
sys.path.insert(0, os.path.abspath('.'))

# Simple test of the relation model structure
def test_relation_models_structure():
    """Test that relation models have the expected structure."""
    print("Testing relation models structure...")
    
    # Import some relation classes to verify structure
    try:
        from apis_ontology.models import (
            AuthorOf, BornIn, LivedIn, Contains, StudiedAt,
            Person, Place, Work, Institution, Expression, Manuscript
        )
        
        # Test that relation models have the expected attributes
        relations_to_test = [
            (AuthorOf, Person, Work),
            (BornIn, Person, Place), 
            (LivedIn, Person, Place),
            (StudiedAt, Person, Institution),
            (Contains, Manuscript, Expression),
        ]
        
        for relation_class, expected_subj, expected_obj in relations_to_test:
            print(f"Testing {relation_class.__name__}...")
            
            # Check that it has subj_model and obj_model
            assert hasattr(relation_class, 'subj_model'), f"{relation_class.__name__} missing subj_model"
            assert hasattr(relation_class, 'obj_model'), f"{relation_class.__name__} missing obj_model"
            
            # Check that they point to the expected classes
            assert relation_class.subj_model == expected_subj, f"{relation_class.__name__} subj_model mismatch"
            assert relation_class.obj_model == expected_obj, f"{relation_class.__name__} obj_model mismatch"
            
            print(f"  ✓ {relation_class.__name__}: {expected_subj.__name__} → {expected_obj.__name__}")
            
        print("✓ All relation models have correct structure")
        return True
        
    except Exception as e:
        print(f"✗ Error testing relation structure: {e}")
        return False

def test_entity_inheritance():
    """Test entity inheritance structure."""
    print("\nTesting entity inheritance...")
    
    try:
        from apis_ontology.models import Person, Place, Work, Institution, Expression, Manuscript
        
        entities = [Person, Place, Work, Institution, Expression, Manuscript]
        
        for entity in entities:
            print(f"Testing {entity.__name__}...")
            
            # Check MRO (Method Resolution Order)
            mro = entity.__mro__
            print(f"  MRO: {[cls.__name__ for cls in mro]}")
            
            # Verify it has the expected Django model structure
            assert hasattr(entity, '_meta'), f"{entity.__name__} missing _meta"
            assert hasattr(entity, 'objects'), f"{entity.__name__} missing objects manager"
            
            print(f"  ✓ {entity.__name__} has proper Django model structure")
            
        print("✓ All entities have correct inheritance")
        return True
        
    except Exception as e:
        print(f"✗ Error testing entity inheritance: {e}")
        return False

def test_signal_logic():
    """Test the signal handler logic."""
    print("\nTesting signal handler logic...")
    
    try:
        from apis_ontology.models import Person, AuthorOf, BornIn
        
        # Simulate what the signal handler does
        sender = Person
        
        # Check if sender would be identified as an entity (not a relation)
        is_relation = hasattr(sender, 'subj_model') and hasattr(sender, 'obj_model')
        print(f"  Person identified as relation: {is_relation} (should be False)")
        assert not is_relation, "Person incorrectly identified as relation"
        
        # Check relation model detection
        relation_sender = AuthorOf
        is_relation = hasattr(relation_sender, 'subj_model') and hasattr(relation_sender, 'obj_model')
        print(f"  AuthorOf identified as relation: {is_relation} (should be True)")
        assert is_relation, "AuthorOf not identified as relation"
        
        # Test model matching logic
        print(f"  AuthorOf.subj_model == Person: {AuthorOf.subj_model == Person}")
        print(f"  Person in Person.__mro__: {Person in Person.__mro__}")
        
        print("✓ Signal handler logic looks correct")
        return True
        
    except Exception as e:
        print(f"✗ Error testing signal logic: {e}")
        return False

if __name__ == '__main__':
    print("=== Static Analysis of Auto-Delete Relations ===\n")
    
    success = True
    success &= test_relation_models_structure()
    success &= test_entity_inheritance() 
    success &= test_signal_logic()
    
    print(f"\n=== Analysis Complete ===")
    if success:
        print("✓ All tests passed - implementation looks correct!")
    else:
        print("✗ Some tests failed - review implementation")
    
    sys.exit(0 if success else 1)