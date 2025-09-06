"""Configuration settings for the application."""

import os
from typing import Optional


class Settings:
    """Application settings loaded from environment variables."""
    
    def __init__(self):
        """Initialize settings from environment variables."""
        # Firebase configuration
        self.region: str = os.environ.get("FUNCTIONS_REGION", "europe-west1")
        
        # Authentication
        self.secret: Optional[str] = os.environ.get("SECRET")
        
        # GCP configuration
        self.gcp_project_id: Optional[str] = os.environ.get("GCP_PROJECT_ID")
        self.task_queue_region: Optional[str] = os.environ.get("TASK_QUEUE_REGION")
        self.task_queue_name: Optional[str] = os.environ.get("TASK_QUEUE_NAME")
        
        # Reservation configuration
        self.reservation_exp_time: int = int(os.environ.get("RESERVATION_EXP_TIME", "3600"))  # 1 hour default
        self.reservation_exp_check_url: Optional[str] = os.environ.get("RESERVATION_EXP_CHECK_URL")
        self.task_schedule_delay: int = int(os.environ.get("TASK_SCHEDULE_DELAY", "300"))  # 5 minutes default
        
        # Email configuration
        self.brevo_smtp_api_key: Optional[str] = os.environ.get("BREVO_SMTP_API_KEY")
        self.brevo_smtp_base_url: Optional[str] = os.environ.get("BREVO_SMTP_BASE_URL")
        self.brevo_smtp_sender_email: str = os.environ.get("BREVO_SMTP_SENDER_EMAIL", "davethebrave160691@gmail.com")
        self.brevo_smtp_sender_name: str = os.environ.get("BREVO_SMT_SENDER_NAME", "The VisitHome Team")
    
    def validate(self) -> None:
        """Validate that all required settings are present."""
        required_settings = [
            ("SECRET", self.secret),
            ("GCP_PROJECT_ID", self.gcp_project_id),
            ("TASK_QUEUE_REGION", self.task_queue_region),
            ("TASK_QUEUE_NAME", self.task_queue_name),
            ("RESERVATION_EXP_CHECK_URL", self.reservation_exp_check_url),
            ("BREVO_SMTP_API_KEY", self.brevo_smtp_api_key),
            ("BREVO_SMTP_BASE_URL", self.brevo_smtp_base_url),
        ]
        
        missing_settings = [name for name, value in required_settings if not value]
        
        if missing_settings:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_settings)}")


# Global settings instance
settings = Settings()
