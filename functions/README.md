# Chome Firebase Functions

A refactored Firebase Functions project for the Chome application, following Python best practices and clean architecture principles.

## Project Structure

```
functions/
├── src/
│   └── chome_functions/
│       ├── __init__.py
│       ├── main.py                 # Main Firebase Functions
│       ├── config/
│       │   ├── __init__.py
│       │   └── settings.py         # Configuration management
│       ├── utils/
│       │   ├── __init__.py
│       │   ├── firestore_client.py # Firestore client utilities
│       │   └── logging.py          # Logging utilities
│       ├── auth/
│       │   ├── __init__.py
│       │   └── auth_service.py     # Authentication service
│       ├── events/
│       │   ├── __init__.py
│       │   └── event_service.py    # Event management service
│       ├── reservations/
│       │   ├── __init__.py
│       │   └── reservation_service.py # Reservation management service
│       └── email/
│           ├── __init__.py
│           └── email_service.py    # Email service using Brevo API
├── tests/                          # Test directory
├── main.py                         # Entry point for Firebase Functions
├── requirements.txt                # Python dependencies
├── setup.py                       # Package setup
└── README.md                      # This file
```

## Features

### Firebase Functions

1. **Reservation Management**
   - `on_reservation_created`: Schedules expiration check for new reservations
   - `on_reservation_confirmed`: Sends confirmation email when reservation is confirmed
   - `verify_reservation_expiration`: HTTP endpoint to check reservation expiration

2. **Event Management**
   - `on_event_created`: Duplicates event associations for duplicate events
   - `on_event_delete`: Cleans up associated questions and media when event is deleted

3. **User Management**
   - `on_user_created`: Ensures proper name field formatting for new users

### Services

- **AuthService**: Handles authentication and token verification
- **EventService**: Manages event-related operations (duplication, deletion)
- **ReservationService**: Handles reservation operations and expiration checks
- **EmailService**: Sends emails using Brevo API

## Configuration

The application uses environment variables for configuration. Required variables:

```bash
# Authentication
SECRET=your_secret_token

# GCP Configuration
GCP_PROJECT_ID=your_project_id
TASK_QUEUE_REGION=your_region
TASK_QUEUE_NAME=your_queue_name

# Reservation Configuration
RESERVATION_EXP_TIME=3600  # seconds
RESERVATION_EXP_CHECK_URL=https://your-function-url
TASK_SCHEDULE_DELAY=300    # seconds

# Email Configuration (Brevo)
BREVO_SMTP_API_KEY=your_api_key
BREVO_SMTP_BASE_URL=https://api.brevo.com/v3
BREVO_SMTP_SENDER_EMAIL=your_email@example.com
BREVO_SMTP_SENDER_NAME=Your Name
```

## Installation

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables (see Configuration section)

## Development

### Code Style

The project follows PEP 8 guidelines and uses:
- 4 spaces for indentation
- Type hints for all functions
- Comprehensive error handling
- Structured logging
- Clean architecture principles

### Testing

Run tests with:
```bash
pytest tests/
```

### Deployment

Deploy to Firebase:
```bash
firebase deploy --only functions
```

## Architecture

The refactored code follows these principles:

1. **Separation of Concerns**: Each module has a single responsibility
2. **Dependency Injection**: Services are injected where needed
3. **Error Handling**: Comprehensive error handling with proper logging
4. **Type Safety**: Full type hints throughout the codebase
5. **Configuration Management**: Centralized configuration with validation
6. **Logging**: Structured logging for better debugging and monitoring

## Migration from Old Code

The refactored code maintains full backward compatibility with the original Firebase Functions. All function signatures and behaviors remain the same, but the internal implementation has been improved for:

- Better error handling
- Improved logging
- Cleaner code structure
- Better maintainability
- Type safety
- Configuration management
