# Chome Firebase Functions

A refactored Firebase Cloud Functions project built with Python following best practices. Provides backend services for event management, reservation systems, and automated email notifications.

## 🚀 Features 

### Event Management
- **Event Creation**: Automatic handling of event creation with duplication support
- **Event Duplication**: Clone events with all associated questions and media files
- **Event Deletion**: Clean removal of events with automatic cleanup of associations
- **Media Management**: Automatic file duplication and deletion in Google Cloud Storage
- **Location Services**: Automatic geohash generation for location-based queries

### Reservation System
- **Reservation Creation**: Automatic scheduling of expiration checks for new reservations
- **Reservation Confirmation**: Email notifications when reservations are confirmed
- **Expiration Management**: Automated cleanup of expired reservations using Cloud Tasks
- **Status Tracking**: Real-time monitoring of reservation status changes

### Email Notifications
- **Automatic Triggers**: Emails sent automatically on reservation confirmation
- **Professional Templates**: Beautiful HTML and plain text email templates
- **Brevo Integration**: Reliable email delivery using Brevo SMTP API
- **Error Handling**: Comprehensive error handling and retry logic

### Authentication & Security
- **Token Verification**: Secure API endpoints with token-based authentication
- **Environment Configuration**: Centralized configuration management
- **Input Validation**: Comprehensive input validation and sanitization

### Location Services
- **Geohash Generation**: Automatic geohash creation for event coordinates
- **Location Queries**: Support for efficient location-based searches
- **Coordinate Processing**: Handles both Firebase GeoPoint and dictionary formats
- **Real-time Updates**: Automatic geohash updates when event positions change

## 🏗️ Project Structure

```
chome-firebase-functions/
├── functions/                          # Cloud Functions source code
│   ├── src/                           # Refactored package structure
│   │   ├── main.py                    # Main Firebase Functions
│   │   ├── config/                    # Configuration management
│   │   │   └── settings.py            # Environment variables & validation
│   │   ├── utils/                     # Utility functions
│   │   │   ├── firestore_client.py    # Firestore client management
│   │   │   ├── app_logging.py         # Structured logging
│   │   │   └── geohash.py             # Geohash utilities for location queries
│   │   ├── auth/                      # Authentication service
│   │   │   └── auth_service.py        # Token verification
│   │   ├── events/                    # Event management service
│   │   │   └── event_service.py       # Event operations & geohash processing
│   │   ├── reservations/              # Reservation management service
│   │   │   └── reservation_service.py # Reservation operations
│   │   └── email/                     # Email service
│   │       └── email_service.py       # Brevo email integration
│   ├── tests/                         # Test directory
│   ├── main.py                        # Entry point (imports from src/)
│   ├── requirements.txt               # Python dependencies
│   └── setup.py                       # Package setup
├── api_docs/                          # API documentation (Bruno)
├── firebase.json                      # Firebase configuration
├── firestore.rules                    # Firestore security rules
├── firestore.indexes.json             # Firestore indexes
├── storage.rules                      # Storage security rules
└── cors.json                          # CORS configuration for Cloud Storage
```

## 🛠️ Prerequisites

- Python 3.8+
- Firebase CLI
- Google Cloud SDK
- Firebase project with Firestore and Storage enabled
- Brevo account with SMTP API access
- Domain verification (for custom sender emails)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd chome-firebase-functions
   ```

2. **Install Firebase CLI**
   ```bash
   npm install -g firebase-tools
   ```

3. **Install Google Cloud SDK**
   ```bash
   # Follow instructions at: https://cloud.google.com/sdk/docs/install
   ```

4. **Login to Firebase**
   ```bash
   firebase login
   ```

5. **Authenticate with gcloud (required for gsutil)**
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
   This will open your browser → choose the account with access to your Firebase project.

6. **Verify you're using the correct project**
   Find your project ID:
   ```bash
   firebase projects:list
   ```
   Then select it:
   ```bash
   gcloud config set project <PROJECT_ID>
   ```

7. **Set up Python environment**
   ```bash
   cd functions
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

## 📦 Dependencies

### Core Dependencies
- **firebase-functions**: Firebase Cloud Functions framework
- **firebase-admin**: Firebase Admin SDK
- **google-cloud-firestore**: Firestore database client
- **pygeohash**: Geohash encoding/decoding for location queries

### Additional Dependencies
- **requests**: HTTP client for API calls
- **python-dotenv**: Environment variable management
- **typing-extensions**: Enhanced type hints support

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the `functions/` directory with the following variables:

```bash
# Authentication
SECRET=your_secret_token_here

# GCP Configuration
GCP_PROJECT_ID=your_project_id
TASK_QUEUE_REGION=europe-west1
TASK_QUEUE_NAME=your_queue_name

# Reservation Configuration
RESERVATION_EXP_TIME=3600
RESERVATION_EXP_CHECK_URL=https://your-function-url.com/verify_reservation_expiration
TASK_SCHEDULE_DELAY=300

# Email Configuration (Brevo)
BREVO_SMTP_API_KEY=your_brevo_api_key
BREVO_SMTP_BASE_URL=https://api.brevo.com/v3
BREVO_SMTP_SENDER_EMAIL=your_email@example.com
BREVO_SMTP_SENDER_NAME=Your Name

# Firebase Functions Region
FUNCTIONS_REGION=europe-west1
```

### Firebase Project Setup

1. **Set up Firebase project**
   ```bash
   firebase use --add
   ```

2. **Enable required services**
   - Firestore Database
   - Cloud Storage
   - Cloud Functions
   - Cloud Tasks (for reservation expiration)

### CORS Configuration for Cloud Storage

To allow cross-origin requests to your Firebase Cloud Storage bucket, you need to configure CORS settings:

1. **Configure CORS for your storage bucket**
   ```bash
   gsutil cors set cors.json gs://<your-cloud-storage-bucket>
   ```

2. **Verify CORS configuration**
   ```bash
   gsutil cors get gs://<your-cloud-storage-bucket>
   ```

3. **Current CORS configuration** (`cors.json`):
   ```json
   [
     {
       "origin": ["*"],
       "method": ["GET"],
       "maxAgeSeconds": 3600
     }
   ]
   ```

   This configuration allows:
   - All origins (`*`) to make requests
   - Only GET requests (for reading files)
   - 1 hour cache for preflight requests

4. **For production**, consider restricting origins:
   ```json
   [
     {
       "origin": ["https://yourdomain.com", "https://www.yourdomain.com"],
       "method": ["GET", "POST", "PUT", "DELETE"],
       "maxAgeSeconds": 3600
     }
   ]
   ```

## 🚀 Development

### Running Locally

1. **Start Firebase emulators**
   ```bash
   cd functions
   source venv/bin/activate
   firebase emulators:start
   ```

2. **Functions will be available at:**
   - Functions: `http://localhost:5001`
   - Firestore: `http://localhost:8080`
   - Emulator UI: `http://localhost:4000`

### Testing

The project includes Bruno API documentation for testing endpoints:
- Navigate to `api_docs/Chome Firebase Function/`
- Use Bruno to test the various API endpoints

## 📡 Firebase Functions

### Event Management Functions

#### `on_event_created`
- **Trigger**: Firestore document creation
- **Path**: `event/{event_id}`
- **Purpose**: Handles new event creation and duplication logic
- **Features**:
  - Detects if event is a duplicate (`duplicateFrom` field)
  - Automatically duplicates event associations (questions, media)
  - Logs event creation with details

#### `on_event_delete`
- **Trigger**: Firestore document deletion
- **Path**: `event/{event_id}`
- **Purpose**: Cleans up event associations when event is deleted
- **Features**:
  - Deletes all associated survey questions
  - Removes all associated media files from storage
  - Cleans up database references

### Reservation Management Functions

#### `on_reservation_created`
- **Trigger**: Firestore document creation
- **Path**: `event_reservation/{res_id}`
- **Purpose**: Schedules expiration check for new reservations
- **Features**:
  - Creates Cloud Task for expiration check
  - Configurable delay before expiration check
  - Logs reservation creation details

#### `on_reservation_confirmed`
- **Trigger**: Firestore document update
- **Path**: `event_reservation/{res_id}`
- **Purpose**: Sends confirmation email when reservation is confirmed
- **Features**:
  - Detects `confirmed` field change from `false` to `true`
  - Gathers user, event, and reservation data
  - Sends professional confirmation email
  - Comprehensive error handling

#### `verify_reservation_expiration`
- **Type**: HTTP function
- **Method**: GET
- **Purpose**: Checks if a reservation has expired
- **Features**:
  - Requires authentication token
  - Validates reservation existence
  - Checks expiration based on creation time
  - Deletes expired reservations
  - Returns appropriate status codes

### User Management Functions

#### `on_user_created`
- **Trigger**: Firestore document creation
- **Path**: `user/{user_id}`
- **Purpose**: Ensures consistent user name field formatting
- **Features**:
  - Creates `firstName` and `lastName` from `display_name`
  - Creates `display_name` from `firstName` and `lastName`
  - Handles single name scenarios
  - Updates user document automatically

### Location Services Functions

#### `on_event_position_updated`
- **Trigger**: Firestore document update
- **Path**: `event/{event_id}`
- **Purpose**: Automatically generates and updates geohash for location-based queries
- **Features**:
  - Detects changes to the `position` field
  - Supports both Firebase GeoPoint and dictionary formats
  - Generates 10-character precision geohash
  - Updates document with `geohash` field
  - Handles coordinate validation and error cases

#### Geohash Processing (in `on_event_created`)
- **Trigger**: Firestore document creation
- **Path**: `event/{event_id}`
- **Purpose**: Generates geohash for new events with position data
- **Features**:
  - Processes position data during event creation
  - Works for both new events and duplicated events
  - Automatic geohash generation and storage
  - Supports efficient location-based queries

## 📧 Email Service Features

### Automatic Email Triggers
- **Reservation Confirmation**: Sent when `confirmed` field changes to `true`
- **Professional Templates**: Beautiful HTML with plain text fallback
- **Event Details**: Includes event name, date, location, and reservation ID
- **Responsive Design**: Works on all devices and email clients

### Email Content
- **Subject**: "Reservation Confirmed - {Event Name}"
- **HTML Template**: Professional design with event details
- **Plain Text**: Fallback for email clients that don't support HTML
- **Branding**: Customizable sender name and email

### Configuration
```bash
# Required for email functionality
BREVO_SMTP_API_KEY=your_brevo_api_key
BREVO_SMTP_BASE_URL=https://api.brevo.com/v3
BREVO_SMTP_SENDER_EMAIL=your_verified_email@domain.com
BREVO_SMTP_SENDER_NAME=Your Brand Name
```

### Domain Verification
Before using custom sender domains, verify your domain in Brevo:
1. Go to Brevo Dashboard → Senders & IP → Senders
2. Add your domain and follow verification process
3. Add DNS records to your domain
4. Wait for verification (24-48 hours)

## 🔒 Security Features

### Authentication
- **Token-based**: All HTTP endpoints require valid authentication token
- **Environment Variables**: Sensitive data stored in environment variables
- **Input Validation**: Comprehensive validation of all inputs

### Firestore Security
- **Rules**: Configured in `firestore.rules`
- **Indexes**: Optimized queries in `firestore.indexes.json`
- **Access Control**: Proper user and admin access controls

### Storage Security
- **Rules**: Configured in `storage.rules`
- **File Validation**: Proper file type and size validation
- **Access Control**: Secure file access patterns

## 🚀 Deployment

### Deploy Everything
```bash
# Deploy all services (functions, firestore rules, firestore indexes, storage rules)
firebase deploy
```

### Deploy Individual Services
```bash
# Deploy only Firebase Functions
firebase deploy --only functions

# Deploy only Firestore rules
firebase deploy --only firestore:rules

# Deploy only Firestore indexes
firebase deploy --only firestore:indexes

# Deploy only Storage rules
firebase deploy --only storage

# Deploy specific function
firebase deploy --only functions:functionName
```

### Deploy with Environment Variables
```bash
# Set environment variables (if using Firebase Functions config)
firebase functions:config:set secret.key="your_secret"
firebase deploy --only functions
```

### Production Checklist
- [ ] Set all required environment variables
- [ ] Configure proper IAM permissions
- [ ] Set up monitoring and logging
- [ ] Configure function timeout and memory limits
- [ ] Test all functions thoroughly
- [ ] Verify email service configuration

## 📊 Monitoring & Logging

### Structured Logging
- **Levels**: INFO, WARNING, ERROR with appropriate context
- **Format**: Timestamp, module, level, message
- **Context**: Function names, user IDs, operation details

### Monitoring
- **Firebase Console**: View function logs and metrics
- **Cloud Logging**: Advanced log analysis and filtering
- **Alerts**: Set up alerts for function failures
- **Performance**: Monitor execution time and memory usage

## 🧪 Testing

### Unit Tests
```bash
cd functions
source venv/bin/activate
python -m pytest tests/ -v
```

### Test Coverage
```bash
python -m pytest tests/ --cov=src --cov-report=html
```

### Available Tests
- **Authentication Tests**: Token verification and validation
- **Geohash Tests**: Location encoding and decoding functionality
- **Environment Tests**: Configuration validation
- **Import Tests**: Module import verification

### Integration Testing
- Use Bruno API documentation for endpoint testing
- Test with Firebase emulators for local development
- Verify email functionality with test accounts

## 🔧 Development Features

### Code Quality
- **Type Hints**: Full type annotations throughout codebase
- **Error Handling**: Comprehensive error handling and logging
- **Clean Architecture**: Separation of concerns with service classes
- **Documentation**: Comprehensive docstrings and comments

### Development Tools
- **Linting**: Code quality checks and formatting
- **Testing**: Unit and integration test framework
- **Logging**: Structured logging for debugging
- **Configuration**: Centralized configuration management

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes following the code style
4. Add tests for new functionality
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Check Firebase documentation
- Review function logs in Firebase Console
- Open an issue in the repository
- Check the troubleshooting section below

## 🔗 Useful Links

- [Firebase Functions Documentation](https://firebase.google.com/docs/functions)
- [Python Functions Guide](https://firebase.google.com/docs/functions/get-started?gen=python)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Google Cloud Tasks](https://cloud.google.com/tasks/docs)
- [Brevo SMTP API](https://developers.brevo.com/reference/sendtransacemail)