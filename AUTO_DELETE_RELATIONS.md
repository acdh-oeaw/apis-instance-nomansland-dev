# Auto-Delete Relations Feature

## Overview

This feature automatically deletes relations when their subject or object entities are deleted, maintaining data integrity and preventing orphaned relations.

## How It Works

When an entity (Person, Place, Institution, Work, Expression, Manuscript, etc.) is deleted, the system automatically:

1. Identifies all relations where the deleted entity is the subject
2. Identifies all relations where the deleted entity is the object  
3. Deletes all these relations to prevent orphaned references

## Implementation Details

### Signal Handler

The feature is implemented using Django's `post_delete` signal in `apis_ontology/signals.py`:

- Listens for deletion of any model in the `apis_ontology` app
- Excludes relation models themselves to avoid recursive deletion
- Queries all relation models to find those referencing the deleted entity
- Deletes matching relations using `subj_object_id` and `obj_object_id` fields

### App Configuration

The signal handlers are automatically loaded through the Django app configuration in `apis_ontology/apps.py`.

### Logging

The system logs all relation deletions for auditing purposes:
- Number of relations deleted per relation type
- Total count of deleted relations
- Entity details (type and ID)

## Examples

### Person Deletion
When a Person is deleted, all relations where that person is involved are automatically removed:
- `AuthorOf` relations (person → work)
- `BornIn` relations (person → place)
- `StudiedAt` relations (person → institution)
- etc.

### Place Deletion  
When a Place is deleted, relations are cleaned up:
- `BornIn` relations (person → place)
- `LivedIn` relations (person → place)
- etc.

### Work Deletion
When a Work is deleted:
- `AuthorOf` relations (person → work)
- `ContainsCopyOf` relations (manuscript → work)
- etc.

## Testing

Comprehensive tests are provided in `apis_ontology/tests/test_auto_delete_relations.py` covering:

- Person-Place relations
- Person-Work relations  
- Person-Institution relations
- Manuscript-Expression relations
- Multiple relations per entity
- Verification that only relevant relations are deleted

## Performance Considerations

- The feature only activates on entity deletion (not creation/update)
- Queries are filtered by entity type for efficiency
- Bulk deletion is used when multiple relations need removal
- Logging can be disabled in production if needed for performance

## Backwards Compatibility

This feature is additive and doesn't change existing database schema or API behavior. It only adds automatic cleanup functionality that was previously manual.