# Chome Firebase Functions

A Firebase Cloud Functions project built with Python that provides backend services for event management and reservation systems.

## 🚀 Features

- **Event Management**: Create, duplicate, and delete events with automatic association handling
- **Reservation System**: Handle event reservations with expiration checks and confirmations
- **Email Notifications**: Automatic email confirmations using Brevo SMTP API
- **Authentication**: Token verification for secure API endpoints
- **Cloud Tasks Integration**: Scheduled tasks for reservation expiration management
- **Firestore Triggers**: Automatic document change handling

## 🏗️ Project Structure

```
chome-firebase-functions/
├── functions/                 # Cloud Functions source code
│   ├── main.py              # Main function definitions
│   ├── auth.py              # Authentication utilities
│   ├── events.py            # Event management functions
│   ├── reservations.py      # Reservation handling functions
│   ├── email_service.py     # Centralized email service (Brevo)
│   └── requirements.txt     # Python dependencies
├── api_docs/                # API documentation (Bruno)
├── firebase.json            # Firebase configuration
├── firestore.rules          # Firestore security rules
├── firestore.indexes.json   # Firestore indexes
└── storage.rules            # Storage security rules
```

## 🛠️ Prerequisites

- Python 3.9+
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

3. **Login to Firebase**
   ```bash
   firebase login
   ```

4. **Install Python dependencies**
   ```bash
   cd functions
   pip install -r requirements.txt
   ```

## 🔧 Configuration

1. **Set up Firebase project**
   ```bash
   firebase use --add
   ```

2. **Configure environment variables** (if needed)
   - Create a `.env` file in the `functions/` directory
   - Add any required environment variables

## 🚀 Development

### Running Locally

1. **Start Firebase emulators**
   ```bash
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

## 📡 API Endpoints

### HTTP Functions

- **`on_reservation_confirmed`** - Triggered when a reservation is confirmed
  - Document path: `event_reservation/{res_id}`
  - Trigger: When `confirmed` field changes to `true`
  - Region: `europe-west1`

- **`verify_reservation_expiration`** - Check reservation expiration
  - Method: GET
  - Query params: `res_id`
  - Authentication: Required
  - Region: `europe-west1`

### Firestore Triggers

- **`on_event_created`** - Triggered when an event document is created
  - Document path: `event/{event_id}`
  - Handles event duplication logic

- **`on_event_delete`** - Triggered when an event document is deleted
  - Document path: `event/{event_id}`
  - Cleans up event associations

- **`on_reservation_created`** - Triggered when a reservation is created
  - Document path: `event_reservation/{res_id}`
  - Schedules expiration checks

## 📧 Email Service

### Overview
The project includes a centralized email service using Brevo SMTP API for sending automatic email notifications. The service is primarily used for sending reservation confirmation emails when a reservation is marked as confirmed.

### Features
- **Centralized Service**: Single `email_service.py` file handling all email operations
- **Brevo Integration**: Uses Brevo SMTP API for reliable email delivery
- **Professional Templates**: Beautiful HTML and plain text email templates
- **Automatic Triggering**: Emails are sent automatically when reservations are confirmed
- **Error Handling**: Comprehensive error handling and logging

### How It Works
1. **Trigger**: When an `event_reservation` document is updated and the `confirmed` field changes from `false/undefined` to `true`
2. **Data Collection**: The service gathers reservation, user, and event information from Firestore
3. **Email Generation**: Creates professional HTML and plain text email content
4. **Delivery**: Sends the email via Brevo SMTP API
5. **Logging**: Provides detailed logging for debugging and monitoring

### Email Content
The confirmation emails include:
- **Event Details**: Name, date, and address
- **Reservation Information**: Reservation ID and confirmation status
- **Professional Design**: Responsive HTML template with fallback plain text
- **Branding**: Customizable sender name and email address

### Configuration Required
```bash
# Brevo Email Service Configuration
BREVO_SMTP_API_KEY=your_brevo_smtp_api_key
BREVO_SMTP_BASE_URL=https://api.brevo.com/v3
SENDER_EMAIL=your_verified_email@domain.com
SENDER_NAME=Chome System
```

### Domain Verification
**Important**: Before using custom sender domains (e.g., `noreply@yourdomain.com`), you must verify your domain in Brevo:
1. Go to Brevo Dashboard → Senders & IP → Senders
2. Add your domain and follow the verification process
3. Add the provided DNS records to your domain
4. Wait for verification (can take 24-48 hours)

### Testing
Test the email service by updating a reservation document:
```javascript
// In your frontend or admin panel
await updateDoc(doc(db, 'event_reservation', 'reservation_id'), {
  confirmed: true
});

// The confirmation email will be sent automatically!
```

## 🚀 Deployment

### Deploy to Firebase

1. **Deploy functions only**
   ```bash
   firebase deploy --only functions
   ```

2. **Deploy everything**
   ```bash
   firebase deploy
   ```

3. **Deploy specific functions**
   ```bash
   firebase deploy --only functions:functionName
   ```

### Production Considerations

- Ensure proper environment variables are set
- Configure appropriate IAM permissions
- Set up monitoring and logging
- Consider function timeout and memory limits

## 🔒 Security

- **Firestore Rules**: Configured in `firestore.rules`
- **Storage Rules**: Configured in `storage.rules`
- **Authentication**: Token verification for sensitive endpoints
- **CORS**: Configure as needed for your frontend

## 📊 Monitoring

- **Logs**: View function logs in Firebase Console
- **Metrics**: Monitor function performance and errors
- **Alerts**: Set up alerts for function failures

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📝 License

[Add your license information here]

## 🆘 Support

For issues and questions:
- Check Firebase documentation
- Review function logs
- Open an issue in the repository

## 🔗 Useful Links

- [Firebase Functions Documentation](https://firebase.google.com/docs/functions)
- [Python Functions Guide](https://firebase.google.com/docs/functions/get-started?gen=python)
- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Google Cloud Tasks](https://cloud.google.com/tasks/docs)
