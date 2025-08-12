# Chome Firebase Functions

A Firebase Cloud Functions project built with Python that provides backend services for event management and reservation systems.

## 🚀 Features

- **Event Management**: Create, duplicate, and delete events with automatic association handling
- **Reservation System**: Handle event reservations with expiration checks and confirmations
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

- **`on_complete_reservation`** - Complete a reservation
  - Method: GET
  - Query params: `res_id`
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
