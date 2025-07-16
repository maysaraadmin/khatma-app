# Khatma App

A collaborative Quran reading application that allows users to organize group Quran readings (Khatmas) and track progress.

## Features

- **Khatma Management**: Create, join, and manage Quran reading groups
- **Quran Reading**: Read the Quran with various display options
- **Audio Recitations**: Listen to Quran recitations from various reciters
- **Memorial Khatmas**: Create Khatmas dedicated to deceased individuals
- **Social Features**: Community leaderboard, achievements, and notifications
- **User Profiles**: Personalized profiles with reading statistics and achievements

## Project Structure

The project is organized into several Django apps:

- **core**: Central functionality and shared components
- **users**: User profiles and authentication
- **khatma**: Khatma creation and management
- **quran**: Quran text, recitations, and reading features
- **groups**: Reading groups management
- **notifications**: User notifications system
- **chat**: Chat functionality for groups and Khatmas

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- PostgreSQL (recommended for production) or SQLite (for development)
- pip (Python package manager)

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/khatma-app.git
   cd khatma-app
   ```

2. **Set up a virtual environment**
   ```bash
   python -m venv venv
   # On Windows
   .\venv\Scripts\activate
   # On macOS/Linux
   # source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   - Copy the example environment file:
     ```bash
     copy .env.example .env
     ```
   - Update the `.env` file with your configuration:
     ```env
     # Django Settings
     DJANGO_SECRET_KEY=your-secret-key-here
     DJANGO_DEBUG=True
     DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

     # Database Settings (SQLite for development)
     DATABASE_URL=sqlite:///db.sqlite3
     
     # For production with PostgreSQL:
     # DATABASE_URL=postgres://user:password@localhost:5432/khatma

     # Email Settings
     EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
     DEFAULT_FROM_EMAIL=webmaster@example.com

     # Allauth Settings
     SITE_DOMAIN=localhost:8000
     ACCOUNT_EMAIL_VERIFICATION=optional

     # Google OAuth Settings (optional)
     # SOCIALACCOUNT_PROVIDER_GOOGLE_CLIENT_ID=your-google-client-id
     # SOCIALACCOUNT_PROVIDER_GOOGLE_SECRET=your-google-secret-key
     ```

5. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create a superuser** (admin account)
   ```bash
   python manage.py createsuperuser
   ```

7. **Load initial data**
   ```bash
   python manage.py loaddata quran_data
   ```

8. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   The application will be available at http://127.0.0.1:8000/

### Production Deployment

1. Set `DJANGO_DEBUG=False` in your `.env` file
2. Configure a production database (PostgreSQL recommended)
3. Set up a production web server (Gunicorn + Nginx/Apache)
4. Configure a production email backend
5. Set up SSL/TLS for secure connections
6. Configure proper static and media file serving

Example Gunicorn command:
```bash
gunicorn --workers 3 --bind 0.0.0.0:8000 khatma.wsgi:application


### Staging Deployment

1. Update the `.env` file with staging settings:
   ```
   DJANGO_SETTINGS_MODULE=khatma.settings_staging
   DJANGO_SECRET_KEY=your_staging_secret_key
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=staging.khatma-app.com,staging-khatma-app.herokuapp.com
   SITE_DOMAIN=staging.khatma-app.com

   # Database settings
   DB_NAME=khatma_staging
   DB_USER=khatma_user
   DB_PASSWORD=your-db-password
   DB_HOST=localhost
   DB_PORT=5432

   # Email settings
   EMAIL_HOST=smtp.example.com
   EMAIL_PORT=587
   EMAIL_HOST_USER=your-email@example.com
   EMAIL_HOST_PASSWORD=your-email-password
   DEFAULT_FROM_EMAIL=noreply@khatma-app.com
   ```
2. Install production dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run migrations:
   ```
   python manage.py migrate --settings=khatma.settings_staging
   ```
4. Collect static files:
   ```
   python manage.py collectstatic --noinput --settings=khatma.settings_staging
   ```
5. Deploy to staging server:
   ```
   ./deploy_staging.sh
   ```

### Production Deployment

1. Update the `.env` file with production settings:
   ```
   DJANGO_SETTINGS_MODULE=khatma.settings_production
   DJANGO_SECRET_KEY=your_production_secret_key
   DJANGO_DEBUG=False
   DJANGO_ALLOWED_HOSTS=khatma-app.com,www.khatma-app.com
   SITE_DOMAIN=khatma-app.com
   ```
2. Deploy to production server:
   ```
   ./deploy_production.sh
   ```

## Template Structure

Templates are organized by app:

- `templates/base.html`: Base template (extends core/base.html)
- `core/templates/core/`: Core templates
- `users/templates/users/`: User-related templates
- `khatma/templates/khatma/`: Khatma-related templates
- `quran/templates/quran/`: Quran-related templates
- `groups/templates/groups/`: Group-related templates
- `notifications/templates/notifications/`: Notification templates
- `chat/templates/chat/`: Chat-related templates

## URL Structure

- `/`: Homepage
- `/khatma/`: Khatma-related URLs
- `/quran/`: Quran-related URLs
- `/groups/`: Group-related URLs
- `/users/`: User-related URLs
- `/notifications/`: Notification-related URLs
- `/chat/`: Chat-related URLs

## Models

### Core Models
- `Post`: Social posts for community interactions

### Khatma Models
- `Khatma`: Represents a Quran reading group
- `KhatmaPart`: Individual parts of a Khatma
- `Participant`: Users participating in a Khatma
- `Deceased`: Deceased individuals for memorial Khatmas

### Quran Models
- `QuranPart`: Represents a Juz' (part) of the Quran
- `Surah`: Represents a Surah (chapter) of the Quran
- `Ayah`: Represents an Ayah (verse) of the Quran
- `QuranReciter`: Information about Quran reciters
- `QuranRecitation`: Audio recitations of the Quran

### User Models
- `Profile`: Extended user profile information
- `UserAchievement`: User achievements and badges

### Group Models
- `ReadingGroup`: Reading groups for collaborative study
- `GroupMembership`: User membership in reading groups

### Notification Models
- `Notification`: User notifications for various events

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
