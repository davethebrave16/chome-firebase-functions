# GitHub Actions Workflows

This directory contains GitHub Actions workflows for testing and deploying Firebase Functions.

## Workflows

### 1. Test Workflow (`test.yml`)
- **Triggers**: Pull requests and pushes to `master` and `develop` branches
- **Purpose**: Runs tests and code coverage analysis
- **Environment**: Automatically selects `staging` or `prod` based on branch

### 2. Deploy Workflow (`deploy.yml`)
- **Triggers**: Pushes to `master` and `develop` branches
- **Purpose**: Runs tests, builds, and deploys Firebase Functions
- **Environment**: Automatically selects `staging` or `prod` based on branch

## Environment Configuration

### Branch-to-Environment Mapping
- **`develop` branch** → `staging` environment
- **`master` branch** → `prod` environment

### Required GitHub Secrets

You need to configure the following secrets in your GitHub repository settings for each environment:

#### For Staging Environment (`staging`)
- `SECRET`: Application secret key for staging
- `SMTP_EMAIL`: SMTP email address for staging
- `SMTP_PASSWORD`: SMTP password for staging
- `RESERVATION_EXP_TIME`: Reservation expiration time in seconds (staging)
- `RESERVATION_EXP_CHECK_URL`: Reservation expiration check URL for staging
- `GCP_PROJECT_ID`: Google Cloud Project ID for staging
- `TASK_QUEUE_NAME`: Task queue name for staging
- `TASK_QUEUE_REGION`: Task queue region for staging
- `TASK_SCHEDULE_DELAY`: Task schedule delay in seconds for staging
- `STORAGE_BUCKET`: Google Cloud Storage bucket for staging
- `BREVO_SMTP_API_KEY`: Brevo SMTP API key for staging
- `BREVO_SMTP_BASE_URL`: Brevo SMTP base URL for staging
- `BREVO_SMTP_SENDER_EMAIL`: Brevo sender email for staging
- `BREVO_SMTP_SENDER_NAME`: Brevo sender name for staging
- `FIREBASE_TOKEN`: Firebase deployment token for staging

#### For Production Environment (`prod`)
- `SECRET`: Application secret key for production
- `SMTP_EMAIL`: SMTP email address for production
- `SMTP_PASSWORD`: SMTP password for production
- `RESERVATION_EXP_TIME`: Reservation expiration time in seconds (production)
- `RESERVATION_EXP_CHECK_URL`: Reservation expiration check URL for production
- `GCP_PROJECT_ID`: Google Cloud Project ID for production
- `TASK_QUEUE_NAME`: Task queue name for production
- `TASK_QUEUE_REGION`: Task queue region for production
- `TASK_SCHEDULE_DELAY`: Task schedule delay in seconds for production
- `STORAGE_BUCKET`: Google Cloud Storage bucket for production
- `BREVO_SMTP_API_KEY`: Brevo SMTP API key for production
- `BREVO_SMTP_BASE_URL`: Brevo SMTP base URL for production
- `BREVO_SMTP_SENDER_EMAIL`: Brevo sender email for production
- `BREVO_SMTP_SENDER_NAME`: Brevo sender name for production
- `FIREBASE_TOKEN`: Firebase deployment token for production

## Setting Up GitHub Environments

1. Go to your GitHub repository
2. Navigate to Settings → Environments
3. Create two environments:
   - `staging`
   - `prod`
4. For each environment, add the required secrets listed above
5. Configure environment protection rules as needed

## Workflow Features

### Test Workflow
- Sets up Python 3.12 environment
- Creates virtual environment
- Installs production and development dependencies
- Creates `.env` file from GitHub secrets
- Runs pytest with coverage
- Uploads coverage to Codecov

### Deploy Workflow
- Runs all test steps
- Installs Firebase CLI
- Prepares virtual environment for deployment
- Deploys to Firebase Functions
- Verifies deployment success

## Usage

### Development Workflow
1. Create feature branch from `develop`
2. Make changes and push to feature branch
3. Create pull request to `develop`
4. Tests run automatically on pull request
5. Merge to `develop` triggers deployment to staging

### Production Workflow
1. Merge `develop` to `master`
2. Push to `master` triggers deployment to production
3. All tests must pass before deployment

## Environment Variables

The workflows automatically create a `.env` file in the `functions` directory with all the required environment variables from GitHub secrets. This ensures that your Firebase Functions have access to the correct configuration for each environment.

## Troubleshooting

### Common Issues
1. **Missing secrets**: Ensure all required secrets are configured in the GitHub environment
2. **Firebase authentication**: Verify that the Firebase token and project ID are correct
3. **Python dependencies**: Check that `requirements.txt` and `requirements-dev.txt` are up to date
4. **Virtual environment**: The workflow creates a fresh virtual environment for each run

### Debugging
- Check the GitHub Actions logs for detailed error messages
- Verify that all secrets are properly configured
- Ensure the Firebase project ID matches the environment
- Check that the Firebase token has the necessary permissions
