# Khatma Project Structure

This document outlines the organized structure of the Khatma Django application project.

## Root Level

- **manage.py** - Django management script for running commands
- **requirements.txt** - Python package dependencies
- **README.md** - Project overview and documentation
- **.env.example** - Example environment variables template
- **.gitignore** - Git ignore rules

## Core Directories

### `/khatma_project/`
**Django project configuration**
- Main project settings and configuration files
- WSGI and ASGI application entry points

### `/chat/`
**Chat application module**
- Real-time chat functionality
- WebSocket handlers
- Chat models, views, and serializers

### `/core/`
**Core application module**
- Shared utilities and base classes
- Common middleware
- Core business logic

### `/users/`
**User management application**
- User authentication and profiles
- Permission management
- User-related models and views

### `/groups/`
**Group management application**
- Group creation and management
- Group membership handling
- Group-related business logic

### `/quran/`
**Quran data management application**
- Quranic verses and chapters (Surahs)
- Quranic text data
- Quran-related models and APIs

### `/khatma/`
**Khatma (Quran completion) tracking**
- Tracking Quran reading progress
- Khatma sessions and participants
- Reading schedule management

### `/reciters/`
**Audio reciters management**
- Quran reciter information
- Audio file associations
- Reciter profiles

### `/notifications/`
**Notification system**
- In-app notifications
- Email notifications
- Notification queuing and delivery

### `/social/`
**Social features**
- User interactions
- Sharing functionality
- Social graph management

### `/static/`
**Static files**
- CSS stylesheets
- JavaScript files
- Images and media assets

### `/templates/`
**HTML templates**
- Django template files
- Frontend template structure
- Reusable template components

### `/docs/`
**Documentation and planning**
- Project planning documents
- Implementation guides
- Setup and deployment instructions
- Google OAuth setup documentation
- Refactoring plans and summaries
- Best practices documentation

## Organization Directories

### `/scripts/`
**Utility and management scripts**

#### Database Management
- `check_db.py` - Database integrity checking
- `check_schema.py` - Database schema validation
- `reset_admin.py` - Reset admin user credentials
- `reset_admin_password.py` - Reset admin password

#### Data Import/Export
- `import_quran.py` - Import Quran data
- `import_quran_with_parts.py` - Import with Juz (parts)
- `import_quran_verses.py` - Import individual verses
- `import_quran_verses_to_parts.py` - Map verses to parts
- `import_selected_parts.py` - Import specific parts
- `import_selected_surahs.py` - Import specific chapters
- `import_all_parts.py` - Import all Juz divisions
- `populate_quran_data.py` - Populate Quran database
- `populate_quran_data_from_file.py` - Load from file
- `populate_quran_parts.py` - Populate Juz data
- `populate_all_surahs.py` - Populate all chapters
- `populate_sample_ayahs_for_all_surahs.py` - Sample verses
- `populate_more_ayahs.py` - Add more verses
- `populate_surah_2_ayahs.py` - Populate Surah Al-Baqarah
- `create_quran_data.py` - Create Quran data structure

#### Code Quality & Organization
- `check_code_quality.py` - Code quality analysis
- `standardize_app_structure.py` - Standardize app structure
- `standardize_templates.py` - Standardize templates
- `organize_app.py` - Automated app organization
- `organize_static_files.py` - Organize static files
- `run_all_improvements.py` - Run all improvement scripts
- `enforce_import_ordering.py` - Enforce import order
- `separate_business_logic.py` - Separate business logic
- `convert_to_class_based_views.py` - Convert to class-based views
- `add_docstrings.py` - Add documentation strings
- `optimize_database_queries.py` - Query optimization
- `implement_error_handling.py` - Error handling implementation
- `generate_documentation.py` - Generate API documentation
- `generate_docs.py` - Generate docs

#### Testing & Verification
- `test_django.py` - Django test suite
- `test_google_oauth.py` - OAuth testing
- `run_tests.py` - Test runner
- `check_environment.py` - Environment validation
- `check_requirements.py` - Dependency checking
- `check_quran_data.py` - Quran data validation

#### Integration & Setup
- `add_google_oauth.py` - Google OAuth integration
- `fixed_group_list.py` - Group list fixes
- `prepare_deployment.py` - Deployment preparation

#### Deployment & Server
- `run_server_with_output.bat` - Run server with output (Windows)
- `start_server.bat` - Start development server (Windows)
- `organize_app.bat` - Organize app (Windows batch)
- `switch_environment.sh` - Switch environments (Linux/Mac)

### `/data/`
**Data files and backups**

- `db.backup.sqlite3` - Database backup
- `quran-text.txt` - Quran text file
- `quran_sample.txt` - Sample Quran data
- `add_birth_date.sql` - SQL migration for birth date
- `code_quality_report.json` - Code quality metrics
- `code_quality_summary.json` - Quality summary

### `/deployment/`
**Deployment configuration**

- `Procfile` - Procfile for Heroku/production
- `Procfile.development` - Development Procfile
- `Procfile.production` - Production Procfile
- `Procfile.staging` - Staging Procfile
- `deploy_production.sh` - Production deployment script
- `deploy_staging.sh` - Staging deployment script
- `runtime.txt` - Python runtime specification

### `/config/`
**Configuration files**
- Reserved for future configuration management
- May contain environment-specific config files

### `/tests/`
**Test files and test data**
- Reserved for test suites and test utilities
- May contain test data files

### `/.github/`
**GitHub-specific files**
- Workflow files (.github/workflows)
- Issue templates
- Pull request templates

## Key Files

### `manage.py`
Django management command script. Use for:
```bash
python manage.py runserver      # Start development server
python manage.py migrate        # Apply database migrations
python manage.py createsuperuser # Create admin user
```

### `requirements.txt`
Python package dependencies. Install with:
```bash
pip install -r requirements.txt
```

### `.env.example`
Template for environment variables. Copy and rename to `.env` and update with your settings:
```bash
cp .env.example .env
```

## Usage

### Running Maintenance Scripts
```bash
# From the root directory
python scripts/check_db.py
python scripts/populate_quran_data.py
python scripts/run_tests.py
```

### Deployment
```bash
# See deployment scripts
bash deployment/deploy_staging.sh
bash deployment/deploy_production.sh
```

### Data Management
```bash
# Import Quran data
python scripts/import_quran.py
python scripts/populate_quran_data.py

# Backup database
cp db.sqlite3 data/db.backup.sqlite3
```

## Best Practices

1. **Keep root clean** - Only Django core files and documentation
2. **Use scripts/ for utilities** - All management scripts go here
3. **Organize by feature** - Each Django app handles its domain
4. **Document changes** - Update docs/ with implementation details
5. **Backup data** - Keep backups in data/ directory
6. **Version control** - Use .gitignore appropriately

## Application Relationships

```
khatma_project (Django Project Config)
├── users (User & Auth)
├── chat (Messaging)
├── groups (Group Management)
├── quran (Quran Data)
├── khatma (Quran Reading Tracker)
├── reciters (Audio Reciters)
├── notifications (System Notifications)
├── social (Social Features)
└── core (Shared Utilities)
```

## Next Steps

1. Review and update environment variables in `.env.example`
2. Install dependencies: `pip install -r requirements.txt`
3. Run migrations: `python manage.py migrate`
4. Create superuser: `python manage.py createsuperuser`
5. Start server: `python manage.py runserver`

---

*Last Updated: 2026-08-29*
