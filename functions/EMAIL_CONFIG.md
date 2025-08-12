# Email Service Configuration

## Required Environment Variables

To use the Brevo email service, you need to set the following environment variables:

### Brevo Configuration
- `BREVO_SMTP_API_KEY`: Your Brevo SMTP API key (required)
- `BREVO_SMTP_BASE_URL`: Your Brevo SMTP base URL (required)
- `SENDER_EMAIL`: Email address to send from (defaults to noreply@yourdomain.com)
- `SENDER_NAME`: Name to display as sender (defaults to "Chome System")

### Example Configuration
```bash
# Brevo Email Service
BREVO_SMTP_API_KEY=xkeysib-your-actual-api-key-here
BREVO_SMTP_BASE_URL=https://api.brevo.com/v3
SENDER_EMAIL=noreply@yourdomain.com
SENDER_NAME=Chome System
```

## Getting Your Brevo API Key

1. Sign up/login to [Brevo](https://www.brevo.com/)
2. Go to your account settings
3. Navigate to the API Keys section
4. Generate a new API key with SMTP permissions
5. Copy the API key and set it as the `BREVO_API_KEY` environment variable

## Testing the Email Service

You can test the email service by calling the reservation confirmation endpoint:

```bash
# Test with a reservation ID
curl "https://your-function-url/on_complete_reservation?res_id=YOUR_RESERVATION_ID"
```

## Email Templates

The service supports both:
- **Direct HTML/Text content** (currently implemented)
- **Brevo templates** (can be implemented by passing template_id and template_data)

## Error Handling

The service includes comprehensive error handling:
- API key validation
- Network request error handling
- Response validation
- Detailed logging for debugging

## Security Notes

- Never commit your API key to version control
- Use environment variables or secure secret management
- The API key should have minimal required permissions
- Consider implementing rate limiting for production use
