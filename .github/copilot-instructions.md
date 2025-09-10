# APIS Nomansland Development Instance

APIS (Austrian Prosopographical Information System) instance for the Nomansland project - a Django-based web application for managing historical manuscripts and prosopographical data.

Always reference these instructions first and fallback to search or bash commands only when you encounter unexpected information that does not match the info here.

## Working Effectively

### Environment Setup
- **Python Version**: Requires Python 3.11+ (tested with 3.12.3)
- **Dependencies**: All managed via `pyproject.toml` (NOT requirements.txt)
- **Database**: PostgreSQL required for production, SQLite acceptable for development
- **Framework**: Built on top of apis-core-rdf framework

### Bootstrap and Installation
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies - NETWORK ISSUES COMMON
pip install -e .
```

**CRITICAL DEPENDENCY INSTALLATION ISSUES:**
- PyPI connectivity timeouts are frequent - installation may fail due to network limitations
- If pip install fails with timeout errors, this is a known environment limitation
- Installation typically takes 3-5 minutes when network is working
- NEVER CANCEL: Allow up to 10 minutes for dependency resolution timeouts
- Required packages include: apis-core-rdf==0.49.1, apis-acdhch-default-settings==2.11.0, django>=5, psycopg2

### Alternative Setup (when PyPI fails)
```bash
# Use system Django if available
sudo apt update && sudo apt install -y python3-django python3-pip postgresql-client
# Note: This only provides basic Django - full functionality requires pip dependencies
```

### Django Application Commands
```bash
# Basic Django management (requires dependencies)
python manage.py check
python manage.py migrate
python manage.py runserver

# Settings configuration
export DJANGO_SETTINGS_MODULE=apis_ontology.settings.server_settings
# OR for development without full dependencies:
export DJANGO_SETTINGS_MODULE=apis_ontology.settings.local_dev
```

### Build and Test
```bash
# Database setup - NEVER CANCEL: May take 5-10 minutes
python manage.py migrate

# Run tests - NEVER CANCEL: Takes 2-5 minutes 
python manage.py test

# Check for issues
python manage.py check
```

## Validation Scenarios

### Basic Functionality Testing
Always validate these workflows after making changes:

1. **Django Configuration Check**:
   ```bash
   python manage.py check
   # Should return "System check identified no issues"
   ```

2. **Database Operations**:
   ```bash
   python manage.py migrate
   python manage.py showmigrations
   ```

3. **Custom Management Commands**:
   ```bash
   python manage.py help
   # Should show custom commands like import_data, export_data, setup_collections
   ```

4. **Date Parser Functionality** (when dependencies available):
   ```bash
   python manage.py test apis_ontology.tests.test_date_utils
   # Tests the core nomansland date parsing functionality
   ```

### Network Dependency Validation
```bash
# Test if dependencies are properly installed
python -c "import apis_core; print('APIS Core available')"
python -c "import django_interval; print('Django Interval available')"
```

**Expected Results when fully set up:**
- Application starts on localhost:8000
- Admin interface accessible at /admin/
- Custom management commands work for data import/export

## Project Structure

### Key Directories and Files
```
├── manage.py                    # Django management script
├── pyproject.toml              # Dependencies and build config (NOT requirements.txt)
├── apis_ontology/              # Main Django application
│   ├── settings/
│   │   └── server_settings.py # Production settings
│   ├── management/commands/    # Custom Django commands
│   ├── models.py              # Database models (depends on apis_core)
│   ├── tests/                 # Test suite
│   └── date_utils.py          # Core date parsing functionality
├── data/                      # Data files directory
└── local/                     # Local development files (ignored by git)
```

### Critical Dependencies
- **apis-core-rdf**: Core APIS framework (version 0.49.1)
- **apis-acdhch-default-settings**: ACDH-CH specific Django settings
- **django-interval**: Date interval handling
- **psycopg2**: PostgreSQL adapter
- **django-reversion**: Model versioning
- **pandas**: Data manipulation

## Common Tasks

### Data Management
```bash
# Import data from various sources
python manage.py import_data
python manage.py import_entities
python manage.py import_relations
python manage.py import_zotero

# Export data
python manage.py export_data
python manage.py export-nodes-links.py

# Setup initial collections and properties
python manage.py setup_collections
python manage.py setup_properties
```

### Development Workflow
```bash
# Create and apply migrations after model changes
python manage.py makemigrations
python manage.py migrate

# Start development server
python manage.py runserver 8000
# Access at http://localhost:8000
```

### Troubleshooting

**Common Issues:**
1. **ModuleNotFoundError for apis_core**: Dependencies not installed due to network issues
2. **ALLOWED_HOSTS error**: Set DJANGO_SETTINGS_MODULE or configure ALLOWED_HOSTS
3. **Database connection errors**: PostgreSQL not running or misconfigured
4. **pip timeout errors**: Network connectivity issues with PyPI

**Validation Steps:**
1. Always run `python manage.py check` before starting development
2. Verify virtual environment is activated: `which python` should point to venv
3. Test database connectivity before running migrations
4. Use `python manage.py shell` to test imports interactively

## Known Limitations

### Environment Constraints
- **PyPI Network Issues**: Frequent timeouts during pip install operations
- **Production Dependencies**: Application requires full APIS framework stack
- **Database Requirements**: PostgreSQL for production, SQLite for basic development
- **Complex Setup**: Cannot run without apis-core-rdf and related packages

### Deployment
- **GitHub Actions**: Automated deployment to acdh-ch-dev.oeaw.ac.at
- **Container**: Uses apis-base-container-ref v0.6.4
- **Settings**: Production uses apis_ontology.settings.server_settings

## Quick Reference

### Frequently Used Commands
```bash
# Environment
source venv/bin/activate
export DJANGO_SETTINGS_MODULE=apis_ontology.settings.server_settings

# Development
python manage.py runserver
python manage.py shell
python manage.py check

# Data
python manage.py migrate
python manage.py test
```

### File Locations
- **Settings**: `apis_ontology/settings/server_settings.py`
- **Models**: `apis_ontology/models.py`
- **Tests**: `apis_ontology/tests/`
- **Management Commands**: `apis_ontology/management/commands/`
- **Dependencies**: `pyproject.toml`

Always ensure dependencies are properly installed before attempting to run the application or tests. If network issues prevent installation, document the limitation and proceed with available validation steps.